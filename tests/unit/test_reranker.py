import types
from datetime import date
from src.qabot.search.reranker import Reranker
from src.qabot.schemas.chunk import Chunk, Meta


def make_chunk(name: str, text: str = "t"):
    return Chunk(
        id=f"{name}_0",
        text=text,
        meta=Meta(
            section_id=0,
            section_title="",
            document_title="d",
            path="data/d.pdf",
            tokens=1,
            updated_at=date.today(),
        ),
    )

def stub_reranker(compute_fn):
    r = object.__new__(Reranker)
    r._model = types.SimpleNamespace(compute_score=compute_fn)
    r._batch_size = 8
    return r

def test_empty_candidates_returns_empty():
    r = stub_reranker(lambda pairs, batch_size=None: [])
    out = r.rerank("q", [], top_k=5)
    assert out == []

def test_orders_by_score_desc():
    r = stub_reranker(lambda pairs, batch_size=None: [len(p[1]) for p in pairs])
    a = make_chunk("a", "short")
    b = make_chunk("b", "much longer text")
    out = r.rerank("q", [a, b], top_k=2)
    assert [c.id for c, _ in out] == ["b_0", "a_0"]

def test_top_k_truncates_and_consistent():
    scores = [0.9, 0.2, 0.5, 0.7]
    r = stub_reranker(lambda pairs, batch_size=None: scores)
    items = [make_chunk(f"id{i}") for i in range(len(scores))]
    out = r.rerank("q", items, top_k=2)
    assert len(out) == 2
    assert out[0][1] >= out[1][1]
    out2 = r.rerank("q", items, top_k=2)
    assert [c.id for c, _ in out] == [c.id for c, _ in out2]
