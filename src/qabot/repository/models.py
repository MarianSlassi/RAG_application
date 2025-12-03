from dataclasses import dataclass
from typing import List, Optional

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