from pathlib import Path
import pickle
import numpy as np
import faiss
import re

from rank_bm25 import BM25Okapi
import nltk
from nltk.corpus import stopwords

from src.qabot.schemas import Chunk
from sentence_transformers import SentenceTransformer
from .helpers import Config
from src.qabot.repository.models import ChunkRecord

# ---


nltk.download("stopwords", quiet=True)
STOPWORDS = set(stopwords.words("english"))

class Indexer():
    """Builds and queries a FAISS index over text chunks encoded with SentenceTransformer embeddings."""

    def __init__(self, config: Config | None = None, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2' ):
        """
        Configure index storage and embedding model.

        Args:
            config: Optional `Config`. If omitted, by default instance uses `.index/index.faiss` and `chunks.pkl`.
            model_name: str - SentenceTransformer model identifier used for both indexing and querying.
        """
        self.config = config or Config()
        self.model_name = model_name # Model name for encoding tokens and sentences in vector search
        self._chunks = None
        self._model = None
        self._index_faiss = None
        self._index_bm25 = None
        self._bm25_corpus = None
    
    @staticmethod
    def _tokenize(text: str) -> list[str]:
        tokens = re.findall(r"\b\w+\b", text.lower())
        return [tok for tok in tokens if tok not in STOPWORDS]

    def build_index(self, chunks: list[ChunkRecord]) -> None:
        """
        Encodes the provided text chunks using the SentenceTransformer model, builds a FAISS index from the embeddings,
        writes both the index and the chunks to disk at paths specified in the config, and caches them in memory for future queries.
        Args:
            chunks: list[str] - text chunks from which to build index
        UPD: added bm25 index builder
        """
        chunks_text = [chunk.content for chunk in chunks] # Note that 'chunks' is a list of pydantic scheme objects

        # BM25 index builder
        tokenized_corpus: list[list[str]] = [self._tokenize(text) for text in chunks_text]
        with open(self.config['bm25_file'], "wb") as f:
            pickle.dump(tokenized_corpus,f)
        self._index_bm25 = BM25Okapi(tokenized_corpus)
        self._bm25_corpus = tokenized_corpus

        # FAISS index builder
        model = SentenceTransformer(self.model_name) 
        embeddings = model.encode(chunks_text, convert_to_numpy=True, normalize_embeddings=True)
        dim = embeddings.shape[1]

        index_faiss = faiss.IndexFlatIP(dim)   
        index_faiss.add(embeddings)

        faiss.write_index(index_faiss, str(self.config['index_file']))
        with open(self.config['chunks_file'], "wb") as f:
            pickle.dump(chunks, f)
        
        self._index_faiss = index_faiss
        self._chunks = chunks
        self._model = model
        

    def load_index(self):
        """
        Returns the FAISS index, list of chunks, and embedding model. Loads them from disk if they are not already cached in memory.
        If the index, chunks, and model are already loaded, returns the cached versions without reloading from disk.

        Note:
            Uses config['chunks_file] and config['index_file]
        UPD: returns also _index_bm25
        """
        if all(attr is not None for attr in (self._index_faiss, self._chunks, self._model, self._index_bm25, self._bm25_corpus)):
            return self._index_faiss, self._chunks, self._model, self._index_bm25, self._bm25_corpus
        
        index_faiss = faiss.read_index(str(self.config['index_file']))
        with open(self.config['chunks_file'], "rb") as f:
            chunks = pickle.load(f)

        with open(self.config['bm25_file'], "rb") as f:
            tokenized_corpus_bm25 = pickle.load(f)

        model = SentenceTransformer(self.model_name)
        index_bm25 = BM25Okapi(tokenized_corpus_bm25)

        self._index_faiss = index_faiss
        self._chunks = chunks
        self._model = model
        self._index_bm25 = index_bm25
        self._bm25_corpus = tokenized_corpus_bm25
        

        return index_faiss, chunks, model, index_bm25, tokenized_corpus_bm25

    def query(self, text: str, k: int = 3) ->list[tuple[Chunk, float]]: # Obsolete in terms of usage inside of endpoint, keep as option
        """
        Encodes the input query text using the embedding model, searches the cached or loaded FAISS index for the top k most similar chunks,
        and returns a list of tuples containing (chunk, similarity_score).

        Args:
            text (str): The text query to match against the index.
            k (int): Number of most similar chunks to return.
        """
        index_faiss, chunks, model, index_bm25, tokenized_corpus_bm25 = self.load_index()
        emb = model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        scores, ids = index_faiss.search(emb, k)
        return [(chunks[i], float(scores[0][j])) for j, i in enumerate(ids[0])]
