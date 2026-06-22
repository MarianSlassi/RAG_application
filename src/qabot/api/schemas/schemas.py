from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

# summarize - response
class HistorySummary(BaseModel):
    history_summary: str = Field(..., description="Summary of previous messages, to suit the context limit", examples=["User came with question about weather but model answerd that it doesn\'t know"] )
# summarize - request
class Turn(BaseModel):
    role: Literal['user','assistant'] = Field(..., description="Role of chat participant", examples=["user"])
    content: str = Field(..., description="Message text")

class BaseConversationRequest(HistorySummary):
    session_id: str = Field(..., description="UID of the session", examples=["25eddaa8-c177-49ac-8297-464422c872db"])
    last_turns: list[Turn] = Field(..., description="The exact history of the current conversation", examples=[[{'role':"user", 'content':"Could you be very pleasant?"}, {'role':"assistant", 'content':"Yes, sure"}]])

# /ask - request
class AskRequest(BaseConversationRequest):
    question: str = Field(..., min_length=3, max_length=512, description="User question to the RAG", examples=["How do i reinstall a printer?", "What's the weather today?"])
# /ask - response
class Source(BaseModel):
    title: str # = Field(..., min_length=1, max_length=300, description="Document title")
    path: str # = Field(..., pattern=r"data/.+\.(pdf|md|docx)$", description="Path to file inside the data/ directory")
    updated_at: date
class Timing(BaseModel):
    retrieve_ms: int
    rerank_ms: int
    llm_ms: int
    total_ms: int
class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    timing: Timing

