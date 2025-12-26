from src.qabot.repository.models import ChunkRecord

class ChunkRepository:
    def __init__(self, conn):
        self.conn = conn
    def _ensure_schema(self):
        self.conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id       INTEGER NOT NULL,
            ordinal      INTEGER NOT NULL,
            content      TEXT    NOT NULL,
            tokens_count INTEGER NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
        )
        """
       )
        self.conn.commit() 

    def create(self, record: ChunkRecord):
        self._ensure_schema()
        """
        Returns id of last added row
        """
        cursor = self.conn.execute("""
        INSERT INTO chunks (doc_id, ordinal, content, tokens_count)
        VALUES (?, ?, ?, ?)
        """, (
            record.doc_id,
            record.ordinal,
            record.content,
            record.tokens_count,
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_by_doc_id(self, doc_id: str):
        cur = self.conn.execute("SELECT * FROM logs WHERE doc_id = ?", (doc_id,))
        return [ChunkRecord(**dict(row)) for row in cur.fetchall()]
    
    def get_by_chunk_id(self, chunk_id: str):
        self._ensure_schema()
        cur = self.conn.execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,))
        row = cur.fetchone()
        return ChunkRecord(**dict(row)) if row else None
    
    def delete(self, chunk_id: int) -> int:
        "Used to delete chunk by it's chunk_id"
        self._ensure_schema()
        cur = self.conn.execute("DELETE FROM chunks WHERE chunk_id = ?", (chunk_id,))
        self.conn.commit()
        return cur.rowcount
    
    def delete_by_doc_id(self, doc_id: int) -> int:
        "Used to delete all chunks based on doc_id"
        self._ensure_schema()
        cur = self.conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
        self.conn.commit()
        return cur.rowcount
    