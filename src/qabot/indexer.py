from pathlib import Path
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from src import Config

class Indexer():
    """Builds and queries a FAISS index over text chunks encoded with SentenceTransformer embeddings."""

    def __init__(self, config: Config | None = None, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2' ):
        """Configure index storage and embedding model.

        Args:
            config: Optional `Config`. If omitted, a default instance creates/uses `.index/index.faiss` and `chunks.pkl`.
            model_name: str - SentenceTransformer model identifier used for both indexing and querying.
        """
        self.config = config or Config()
        self.model_name = model_name
        self._index = None
        self._chunks = None
        self._model = None

    def build_index(self, chunks: list[str]) -> None:
        """
        Encodes the provided text chunks using the SentenceTransformer model, builds a FAISS index from the embeddings,
        writes both the index and the chunks to disk at paths specified in the config, and caches them in memory for future queries.
        Args:
            chunks: list[str] - text chunks from which to build index
        """
        model = SentenceTransformer(self.model_name)
        embeddings = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
        dim = embeddings.shape[1]

        index = faiss.IndexFlatIP(dim)   
        index.add(embeddings)

        faiss.write_index(index, str(self.config['index_file']))
        with open(self.config['chunks_file'], "wb") as f:
            pickle.dump(chunks, f)
        self._index = index
        self._chunks = chunks
        self._model = model

    def load_index(self):
        """
        Returns the FAISS index, list of chunks, and embedding model. Loads them from disk if they are not already cached in memory.
        If the index, chunks, and model are already loaded, returns the cached versions without reloading from disk.

        Note:
            Uses config['chunks_file] and config['index_file]
        """
        if self._index is not None and self._chunks is not None and self._model is not None:
            return self._index, self._chunks, self._model
        
        index = faiss.read_index(str(self.config['index_file']))
        with open(self.config['chunks_file'], "rb") as f:
            chunks = pickle.load(f)
        model = SentenceTransformer(self.model_name)
        return index, chunks, model

    def query(self, text: str, k: int = 3):
        """
        Encodes the input query text using the embedding model, searches the cached or loaded FAISS index for the top k most similar chunks,
        and returns a list of tuples containing (chunk, similarity_score).

        Args:
            text (str): The text query to match against the index.
            k (int): Number of most similar chunks to return.
        """
        index, chunks, model = self.load_index()
        emb = model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        scores, ids = index.search(emb, k)
        return [(chunks[i], float(scores[0][j])) for j, i in enumerate(ids[0])]
