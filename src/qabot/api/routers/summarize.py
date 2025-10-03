from fastapi import APIRouter
from pydantic import BaseModel

summarize_router = APIRouter()

class SummarizeRequest(BaseModel):
    session_id: str
    turns: list[dict[str, str]]
    current_summary: str = ""

@summarize_router.post("/summarize")
async def summarize(payload: SummarizeRequest) -> dict[str, str]:
    turns_text = "\n".join(f"{t['role']}: {t['content']}" for t in payload.turns)
    summary = (payload.current_summary + "\n" + turns_text).strip()
    summary = summary[-1000:]  # наивное укорочение
    return {"summary": summary}