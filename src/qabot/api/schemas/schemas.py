from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

class Turn(BaseModel):
    role: Literal['user','assistant']
    content: str

class AskRequest(BaseModel):
    session_id: str = Field(..., description= "UID of the session", examples=["25eddaa8-c177-49ac-8297-464422c872db"])
    question: str = Field(..., min_length=3, max_length=512, description="User question to the RAG", examples=["How do i reinstall a printer?", "What's the weather today?"])
    history_summary: str = Field(..., description="Summary of previous messages, to suit the context limit", examples=["User came with question about weather but model answerd that it doesn't know"])
    last_turns: list[Turn] = Field(..., description="The exact histor of current conversation", examples=[[Turn(role="user",content="Could you be very pleasant?"), Turn(role="assistant",content="Yes, sure")]])

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