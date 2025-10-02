from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

class Turn(BaseModel):
    role: Literal['user','assistant']
    content: str

class AskRequest(BaseModel):
    session_id: str
    question: str = Field(..., min_length=3, max_length=512, description="User question to the RAG", examples=["How do i reinstall a printer?", "What's the weather today?"])
    history_summary: str
    last_turns: list[Turn]

class Source(BaseModel):
    title: str #= Field(..., min_length=1, max_length=300, description="Document title")
    path: str #= Field(..., pattern=r"data/.+\.(pdf|md|docx)$", description="Path to file inside the data/ directory")
    updated_at: date

class Timing(BaseModel):
    retrieve_ms: int
    llm_ms: int
    total_ms: int

class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    timing: Timing

# {
#   "session_id": "uuid",
#   "question": "How do I request equipment?",
#   "history_summary": "User is onboarding, needs laptop.",
#   "last_turns": [
#     {"role": "user", "content": "I’m starting next week."},
#     {"role": "assistant", "content": "…"}
#   ]
# }