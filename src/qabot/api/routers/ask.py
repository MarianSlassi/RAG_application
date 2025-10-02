import time
from fastapi import APIRouter, Request, Depends

from src.qabot.api.schemas import AskRequest
from src.qabot.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.qabot.api.dependencies import get_retriever, get_llm
from src.qabot.api.schemas import Source, Timing, AskResponse
from src.qabot.api.responses import ask_responses

ask_router = APIRouter()
@ask_router.post("/asl", response_model= AskResponse, responses= ask_responses)
async def ask(request: Request, payload: AskRequest, retriever = Depends(get_retriever), llm = Depends(get_llm)):
    perf_total_start = time.perf_counter()

    perf_retrieve_start = time.perf_counter()
    question=payload.question.strip()
    retrieved = retriever.retrieve(question, k=5)
    perf_retrieve_end = time.perf_counter()

    perf_llm_start = time.perf_counter()
    prompt_sources = [{"text": chunk.text, "path": chunk.meta.path} for chunk, i in retrieved]
    user_prompt = USER_PROMPT_TEMPLATE.format(question=question, sources=prompt_sources)
    #perf_llm_start = time.perf_counter()
    answer = llm.generate(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)
    perf_llm_end = time.perf_counter()

    sources = [{'title':chunk.meta.document_title,\
                'path':chunk.meta.path,\
                 'updated_at': chunk.meta.updated_at} for chunk, i in retrieved]
    
    # Removing duplicates from sources
    unique_sources = []
    seen_paths = set()

    for source in sources:
        if source["path"] not in seen_paths:
            unique_sources.append(source)
            seen_paths.add(source["path"])

    # Timings
    perf_total_end = time.perf_counter()
    timing=Timing(
    retrieve_ms =  int( (perf_retrieve_end - perf_retrieve_start) * 1000 ),
    llm_ms = int( (perf_llm_end - perf_llm_start ) * 1000),
    total_ms = int((perf_total_end - perf_total_start ) * 1000)
    )
    endpoint_response = AskResponse(answer= answer, sources= unique_sources, timing= timing)
    return endpoint_response