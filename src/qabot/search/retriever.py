import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import nltk
from nltk.corpus import stopwords
import re
import numpy as np

from ..schemas import Chunk

nltk.download("stopwords", quiet=True)
STOPWORDS = set(stopwords.words("english"))

class Retriever:
    def __init__(self, index: faiss.IndexFlatIP, chunks: list[Chunk], model: SentenceTransformer, index_bm25: BM25Okapi | None, tokenized_corpus_bm25):
        """Class to retrieve data.

        Args:
            index: 
            chunks: 
            model:
            index_bm25:
        """
        if index is None or chunks is None or model is None:
            raise ValueError('Please provide index, chunks, and model to retrieve')
        self._index = index
        self._chunks = chunks
        self._model = model
        self._index_bm25 = index_bm25
        self._tokenized_corpus_bm25 = tokenized_corpus_bm25
    
    def retrieve(self, query: str, k: int = 3, normalize: bool = False) -> list[tuple[Chunk, float]]:
        """
        Encodes the input query text using the embedding model, searches the cached or loaded FAISS index for the top k most similar chunks,
        and returns a list of tuples containing (chunk, similarity_score).

        Args:
            query (str): The text query to match against the index.
            k (int): Number of most similar chunks to return.
        """
        if len(query) <= 3:
            raise ValueError("Text is too short for retrieveng")
        emb = self._model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        scores, ids = self._index.search(emb, k)
        if normalize:
            scores = self._normalize_results(scores[0])
        else:
            scores = scores[0]
        scores = scores.tolist()
        ids = ids[0].tolist()
        return [(self._chunks[i], float(scores[j])) for j, i in enumerate(ids)]
    
    @staticmethod
    def _tokenize(text: str) -> list[str]:
        tokens = re.findall(r"\b\w+\b", text.lower())
        return [tok for tok in tokens if tok not in STOPWORDS]
    
    @staticmethod
    def _normalize_results(scores):
        """
        Min-max normalizer for numpy array
        Returns:
            min-max normalized result
        """
        min_score = scores.min()
        max_score = scores.max()
        denom = max_score - min_score
        if denom == 0:
            normalized = np.zeros_like(scores)
        else:
            normalized = (scores - min_score) / denom
        return normalized

    def bm25_retrieve(self, query:str, k:int=3, normalize: bool=False): # -> list[tuple[Chunk, float]] 
        """
        Tokenize the input query text using self._tokenize(), uses BM25Okapi object to make a search among documents inside of bm25 index 
        Returns normalized scores, usually the top one will have score 1.0 as a maximum and the nex is less, note how it differes from FAISS cos-similarity search scores
        """
        if self._index_bm25 is None:
            raise RuntimeError("BM25 index is not initialized")
        
        tokenize_query = self._tokenize(query)
        
        # scores = self._index_bm25.get_top_n(tokenize_query, documents=[cunk.text for cunk in self._chunks], n=k)
        top_k_documents = self._index_bm25.get_top_n(tokenize_query, documents=self._chunks, n=k)
        scores = self._index_bm25.get_scores(tokenize_query) # Full list of scores in order from the chunks list
        if normalize:
            scores = self._normalize_results(scores)
        scores = np.sort(scores)[::-1][:k] # Reverting to desc sorting and taking only top k chunks
        result = list(zip(top_k_documents, scores.tolist()))
        return result
    
    def hybrid_retrieve(self, query:str, k:int = 5, w_bm25:float = 0.3, w_faiss:float = 0.7) -> list[tuple[Chunk, float]]:
        '''
        Linear combination retrieving algorithm, using faiss and bm25 under the hood.
        '''
        faiss_hits = self.retrieve(query, k=k, normalize=True)
        bm25_hits = self.bm25_retrieve(query, k=k, normalize=True)

        merged: dict[str, dict] = {}
        for chunk, score in faiss_hits:
            merged[chunk.id] = {"chunk": chunk, "faiss": float(score), "bm25": 0.0}
        for chunk, score in bm25_hits:
            merged.setdefault(chunk.id, {"chunk": chunk, "faiss": 0.0, "bm25": 0.0})
            merged[chunk.id]["bm25"] = float(score)

        for entry in merged.values():
            entry["hybrid"] = w_faiss * entry["faiss"] + w_bm25 * entry["bm25"]

        ranked = sorted(merged.values(), key=lambda x: x["hybrid"], reverse=True)
        return [(item["chunk"], item["hybrid"]) for item in ranked[:k]]
 