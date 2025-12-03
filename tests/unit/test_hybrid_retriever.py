import types
import pytest
from src.qabot.search.retriever import Retriever
from src.qabot.schemas.chunk import Chunk, Meta
from datetime import date

def fake_chunk(name):
    return Chunk(id=f"{name}_0", text="t", meta=Meta(section_id=0, section_title="", document_title="d", path="data/d.pdf", tokens=1, updated_at=date.today()))

@pytest.fixture
def hybrid():
    r = object.__new__(Retriever)
    r.retrieve = types.MethodType(lambda self, q, k=5, normalize=True: [
        (fake_chunk("a"), 0.9),
        (fake_chunk("b"), 0.1),
    ], r)
    r.bm25_retrieve = types.MethodType(lambda self, q, k=5, normalize=True: [
        (fake_chunk("b"), 0.8),
    ], r)
    return r

def test_bm25_empty_falls_back_to_faiss(hybrid):
    hybrid.bm25_retrieve = types.MethodType(lambda self, q, k=5, normalize=True: [], hybrid)
    out = hybrid.hybrid_retrieve("q", k=2)
    assert [c.id for c, _ in out] == ["a_0", "b_0"]  

def test_bm25_dominates_when_faiss_weak(hybrid):
    hybrid.retrieve = types.MethodType(lambda self, q, k=5, normalize=True: [(fake_chunk("a"), 0.01)], hybrid)
    hybrid.bm25_retrieve = types.MethodType(lambda self, q, k=5, normalize=True: [(fake_chunk("b"), 0.9)], hybrid)
    out = hybrid.hybrid_retrieve("q", k=1, w_bm25=0.7, w_faiss=0.3)
    assert out[0][0].id == "b_0" 

def test_union_and_truncate(hybrid):
    out = hybrid.hybrid_retrieve("q", k=2)
    assert len(out) == 2
    assert out[0][0].id in {"a_0", "b_0"}
