from fastapi import APIRouter, Depends

from src.qabot.api.schemas.schemas import BaseConversationRequest, HistorySummary
from src.qabot.api.dependencies import get_llm
from src.qabot.llm.prompts import SYSTEM_PROMPT_SUMMARIZE
from src.qabot.helpers.logger import get_custom_logger
logger = get_custom_logger('summarize')
summarize_router = APIRouter()
@summarize_router.post("/summarize")
async def summarize(payload: BaseConversationRequest, llm = Depends(get_llm)) -> HistorySummary:
    logger.info('Request for summarization received')
    logger.debug(f"Payload: {payload}")
    turns_text = "\n".join(f"{t.role}: {t.content}" for t in payload.last_turns)
    summary_turns_text = ( "\nCurrent chat summary:\n" + payload.history_summary + "\nCurrent dialog:\n" + turns_text).strip()
    history_summary = llm.generate(system_prompt =  SYSTEM_PROMPT_SUMMARIZE, user_prompt = summary_turns_text)
    logger.debug(f"Summarized history:  {history_summary}")
    logger.info('Request was summarized')
    return HistorySummary(history_summary=history_summary)
