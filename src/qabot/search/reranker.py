from typing import Iterable
from FlagEmbedding import FlagReranker
from ..schemas import Chunk

class Reranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base", use_fp16: bool = False, device: str | None = None, batch_size: int = 16):
        self._model = FlagReranker(model_name, use_fp16=use_fp16, device=device)
        self._batch_size = batch_size

    def rerank(self, query: str, chunks: list[Chunk], top_k: int = 5) -> list[tuple[Chunk, float]]:
        """
        Takes 'user' query, and a list of 'relevant'
        chunks and gives a list[tuple(Chunk, float)]
        by the cross-encoder model 
        """
        pairs = [(query, chunk.text) for chunk in chunks]
        scores = self._model.compute_score(pairs, batch_size=self._batch_size)
        if scores is None:
            return []
        results = [(chunk, float(score)) for chunk, score in zip(chunks, scores)]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
