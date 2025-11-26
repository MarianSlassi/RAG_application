import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from .models import LogRecord

from src.qabot.helpers.config import Config

class Database:
    @contextmanager
    @staticmethod
    def _connect(db_path):
        conn = sqlite3.connect(db_path, check_same_thread=False)
        try:
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            conn.close()

class LogRepository:
    def __init__(self, conn):
        self.conn = conn
    def _ensure_schema(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        session_id TEXT,
        question TEXT,
        answer TEXT,
        top_doc_paths TEXT,
        answer_length INTEGER,
        retrieve_ms INTEGER,
        llm_ms INTEGER,
        total_ms INTEGER )
        """)
        self.conn.commit() 

    def create(self, record: LogRecord):
        self._ensure_schema()
        """
        Returns id of last added row
        """
        cursor = self.conn.execute("""
        INSERT INTO logs (timestamp, session_id, question, answer, top_doc_paths,
                        answer_length, retrieve_ms, llm_ms, total_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.timestamp,
            record.session_id,
            record.question,
            record.answer,
            json.dumps(record.top_doc_paths),
            record.answer_length,
            record.retrieve_ms,
            record.llm_ms,
            record.total_ms
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_by_session(self, session_id: str):
        cur = self.conn.execute("SELECT * FROM logs WHERE session_id = ?", (session_id,))
        return [LogRecord(**dict(row)) for row in cur.fetchall()]

    def get_by_time_range(self, start: str, end: str):
        cur = self.conn.execute("SELECT * FROM logs WHERE timestamp BETWEEN ? AND ?", (start, end))
        return [LogRecord(**dict(row)) for row in cur.fetchall()]
        
