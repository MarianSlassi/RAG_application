from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime

@dataclass
class LogRecord:
    id: Optional[int] | None
    timestamp: str
    session_id: str
    question: str
    answer: str
    top_doc_paths: List[str]
    answer_length: int
    retrieve_ms: int
    rerank_ms: int
    llm_ms: int
    total_ms: int

@dataclass
class DocumentRecord:
    """Data model for document records."""
    doc_id: Optional[int]           # Assigned automatically by DB
    source_type: str                # Example: "md", "pdf", "docx"
    source_uri: str                 # Local file path
    size_bytes: int                 # File size in bytes
    content_hash: str               # SHA256 of file content
    title: str                      # Document title (filename)
    content: str                    # Full text content
    updated_at: Optional[datetime] = None
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)

@dataclass
class ChunkRecord:
    """Data model for document chunk records."""
    chunk_id: Optional[int]         # Assigned automatically by DB
    doc_id: int                     # Foreign key → parent document
    ordinal: int                    # Order of the chunk in the document (0, 1, 2, ...)
    content: str                    # Text content of the chunk
    tokens_count: int               # Token count in content
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)