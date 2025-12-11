import json
import datetime
from datetime import timedelta
import pytest
from src.qabot.repository.log_repository import LogRepository, Database
from src.qabot.repository.models import LogRecord

def _prepare_repo(tmp_path):
    db_path = tmp_path / "test_logs.db"
    with Database._connect(db_path) as conn:
        repo = LogRepository(conn=conn)
    return repo, db_path

def test_create_and_get_by_session(tmp_path):
    repo, db_path = _prepare_repo(tmp_path)
    with Database._connect(db_path) as conn:
        repo._ensure_schema()
        record = LogRecord(
            id=None,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            session_id="session-42",
            question="Why is the sky blue?",
            answer="Because of Rayleigh scattering.",
            top_doc_paths=["/docs/physics.md", "/docs/optics.md"],
            answer_length=2,
            retrieve_ms=25,
            rerank_ms=98,
            llm_ms=110,
            total_ms=135,
        )
        new_id = repo.create(record)
        rows = repo.get_by_session("session-42")

    assert new_id == 1
    assert len(rows) == 1
    stored = rows[0]
    assert stored.id == 1
    assert stored.session_id == "session-42"
    assert stored.question == record.question
    assert stored.answer == record.answer
    assert stored.top_doc_paths == json.dumps(record.top_doc_paths)
    assert stored.total_ms == record.total_ms

def test_get_by_session_returns_empty_when_not_found(tmp_path):
    repo, db_path = _prepare_repo(tmp_path)
    with Database._connect(db_path) as conn:
        repo._ensure_schema()
        rows = repo.get_by_session("missing-session")
    assert rows == []

def test_get_by_time_range(tmp_path):
    repo, db_path = _prepare_repo(tmp_path)
    now = datetime.datetime.now(datetime.timezone.utc)
    earlier = (now - timedelta(minutes=5)).isoformat()
    later = (now + timedelta(minutes=5)).isoformat()

    with Database._connect(db_path) as conn:
        repo._ensure_schema()
        repo.create(
            LogRecord(
                id=None,
                timestamp=earlier,
                session_id="s1",
                question="Q1",
                answer="A1",
                top_doc_paths=["/doc1"],
                answer_length=1,
                retrieve_ms=10,
                rerank_ms=98,
                llm_ms=20,
                total_ms=30,
            ),
        )
        repo.create(
            LogRecord(
                id=None,
                timestamp=later,
                session_id="s2",
                question="Q2",
                answer="A2",
                top_doc_paths=["/doc2"],
                answer_length=1,
                retrieve_ms=5,
                rerank_ms=24,
                llm_ms=10,
                total_ms=15,
            )
        )
        in_range = repo.get_by_time_range(
            (now - timedelta(minutes=1)).isoformat(),
            (now + timedelta(minutes=1)).isoformat()
        )
        all_rows = repo.get_by_time_range(
            (now - timedelta(hours=1)).isoformat(),
            (now + timedelta(hours=1)).isoformat()
        )
    assert len(in_range) == 0
    assert len(all_rows) == 2
    assert {row.session_id for row in all_rows} == {"s1", "s2"}
