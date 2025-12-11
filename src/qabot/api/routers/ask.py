import time
from fastapi import APIRouter, Request, Depends
import datetime
from transformers import AutoTokenizer

from src.qabot.api.schemas import AskRequest
from src.qabot.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.qabot.api.dependencies.client import get_retriever, get_llm, get_log_repo, get_project_config, get_tokenizer, get_reranker
from src.qabot.api.schemas import Timing, AskResponse
from src.qabot.api.responses import ask_responses
from src.qabot.helpers.logger import get_custom_logger 

from src.qabot.repository.models import LogRecord

logger = get_custom_logger('ask/')

ask_router = APIRouter()
@ask_router.post("/ask", response_model=AskResponse, responses=ask_responses)
def ask(payload: AskRequest, retriever=Depends(get_retriever), llm=Depends(get_llm),
         log_repo=Depends(get_log_repo), project_config=Depends(get_project_config),
           tokenizer=Depends(get_tokenizer), reranker=Depends(get_reranker)):
    perf_total_start = time.perf_counter()
    logger.info(f'Request received: {payload.session_id} ')
    logger.debug(f'Request: \n {payload}')
    perf_retrieve_start = time.perf_counter()
    question = payload.question.strip()
    retrieved = retriever.hybrid_retrieve(question, k=project_config['retriever']['k'])
    chunks = [chunk for chunk, _ in retrieved]
    perf_retrieve_end = time.perf_counter()
    perf_llm_rerank_start = time.perf_counter()
    reranked_chunks = reranker.rerank(query=question, chunks=chunks, top_k=project_config['reranker']['top_k'])
    logger.debug(f"reranked_chunks length!!!:{len(reranked_chunks)}")
    perf_llm_rerank_end = time.perf_counter()
    

    perf_llm_start = time.perf_counter()
    prompt_sources = [{"text": chunk.text, "path": chunk.meta.path} for chunk, _ in reranked_chunks]
    user_prompt = USER_PROMPT_TEMPLATE.format(question=question, sources=prompt_sources)
    #perf_llm_start = time.perf_counter()
    answer = llm.generate(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)
    perf_llm_end = time.perf_counter()

    sources = [{'title':chunk.meta.document_title,
                'path':chunk.meta.path,
                'updated_at': chunk.meta.updated_at} for chunk, _ in reranked_chunks]
    
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
    rerank_ms= int( (perf_llm_rerank_end - perf_llm_rerank_start)  * 1000),
    llm_ms = int( (perf_llm_end - perf_llm_start ) * 1000),
    total_ms = int((perf_total_end - perf_total_start ) * 1000)
    )
    # Database Logging
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        if project_config['web']['backend']['db_logging']: # If db logging enabled in project_config
            log_rec = LogRecord(
                    id = None,
                    timestamp = now_iso,
                    session_id = payload.session_id,
                    question = question,
                    answer = answer,
                    top_doc_paths = [source['path'] for source in unique_sources],
                    answer_length = len(tokenizer.encode(answer)),
                    retrieve_ms = timing.retrieve_ms,
                    rerank_ms=timing.rerank_ms,
                    llm_ms = timing.retrieve_ms,total_ms = timing.total_ms)
            record_id = log_repo.create(log_rec)
            logger.info(f"Created record at database with record_id: {record_id}")
            logger.debug(f"LogRecord which have been created: \n{log_rec}\n")
    except Exception:
        logger.exception('Error while logging model response')


    endpoint_response = AskResponse(answer=answer, sources=unique_sources, timing=timing)
    logger.debug(f'Response: {endpoint_response}')
    return endpoint_response

