from src.qabot.repository.models import DocumentRecord


class DocumentRepository:
    def __init__(self, conn):
        self.conn = conn

    def _ensure_schema(self):
        self.conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            doc_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type  TEXT    NOT NULL,
            source_uri   TEXT    NOT NULL,
            size_bytes   INTEGER NOT NULL,
            content_hash TEXT    NOT NULL,
            title        TEXT    NOT NULL,
            content      TEXT    NOT NULL,
            updated_at   TEXT
        )
        """
       )
        self.conn.commit()

    def create(self, record: DocumentRecord):
        self._ensure_schema()
        """
        Returns id of last added row
        """
        updated_at = record.updated_at
        if updated_at is not None and not isinstance(updated_at, str):
            updated_at = updated_at.isoformat()
        cursor = self.conn.execute("""
        INSERT INTO documents (source_type, source_uri, size_bytes, content_hash, title,
                            content, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            record.source_type,
            record.source_uri,
            record.size_bytes,
            record.content_hash,
            record.title,
            record.content,
            updated_at
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_by_doc_id(self, doc_id: int):
        cur = self.conn.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,))
        row = cur.fetchone()
        return DocumentRecord(**dict(row)) if row else None

    def get_by_source_uri(self, source_uri: str):
        cur = self.conn.execute("SELECT * FROM documents WHERE source_uri = ?", (source_uri,))
        return [DocumentRecord(**dict(row)) for row in cur.fetchall()]

    def delete(self, doc_id: int):
        "Used to delete document by it's id"
        self._ensure_schema()
        cur = self.conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
        self.conn.commit()
        return cur.rowcount

    def delete_by_source_uri(self, source_uri: str):
        "Used to delete document by it's source uri"
        self._ensure_schema()
        cur = self.conn.execute("DELETE FROM documents WHERE source_uri = ?", (source_uri,))
        self.conn.commit()
        return cur.rowcount
