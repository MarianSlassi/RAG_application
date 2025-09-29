import faiss
from sentence_transformers import SentenceTransformer

from src import Chunk

class Retriever:
    def __init__(self, index: faiss.IndexFlatIP, chunks: list[Chunk], model: SentenceTransformer):
        """Class to retrieve data.

        Args:
            index: 
            chunks: 
            model:
        """
        if index is None or chunks is None or model is None:
            raise ValueError('Please provide index, chunks, and model to retrieve')
        self._index = index
        self._chunks = chunks
        self._model = model
    
    def retrieve(self, text: str, k: int = 3):
        """
        Encodes the input query text using the embedding model, searches the cached or loaded FAISS index for the top k most similar chunks,
        and returns a list of tuples containing (chunk, similarity_score).

        Args:
            text (str): The text query to match against the index.
            k (int): Number of most similar chunks to return.
        """
        if len(text) <= 3:
            raise ValueError("Text is too short for retrieveng")
        emb = self._model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        scores, ids = self._index.search(emb, k)
        return [(self._chunks[i], float(scores[0][j])) for j, i in enumerate(ids[0])]