import time
from fastapi import APIRouter, Request, Depends
import datetime
from transformers import AutoTokenizer

from src.qabot.api.schemas import AskRequest
from src.qabot.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.qabot.api.dependencies.client import get_retriever, get_llm, get_db_connection, get_project_config
from src.qabot.api.schemas import Timing, AskResponse
from src.qabot.api.responses import ask_responses
from src.qabot.helpers.logger import get_custom_logger 
from src.qabot.helpers.project_config import load_project_config

from src.qabot.repository.models import LogRecord
from src.qabot.repository.log_repository import LogRepository

logger = get_custom_logger('ask/')

ask_router = APIRouter()
@ask_router.post("/ask", response_model= AskResponse, responses = ask_responses)
def ask(payload: AskRequest, retriever = Depends(get_retriever), llm = Depends(get_llm), connection = Depends(get_db_connection), project_config = Depends(get_project_config)):
    perf_total_start = time.perf_counter()
    logger.info(f'Request received: {payload.session_id}')
    logger.debug(f'Request: \n {payload}')
    perf_retrieve_start = time.perf_counter()
    question = payload.question.strip()
    retrieved = retriever.retrieve(question, k=project_config['retriever']['k'])
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
    # Database Logging
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if project_config['web']['backend']['db_logging']: # If db logging enabled in project_config
        tokenizer = AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        log_rec = LogRecord(id = None, timestamp = now_iso, session_id = payload.session_id, question = question, answer = answer,\
                top_doc_paths = [source['path'] for source in unique_sources], answer_length = len(tokenizer.encode(answer)) ,retrieve_ms = timing.retrieve_ms, llm_ms = timing.retrieve_ms,total_ms = timing.total_ms)
        log_e = LogRepository()
        record_id = log_e.create(log_rec, connection)
        logger.info(f"Created record at database with record_id: {record_id}")
        logger.debug(f"LogRecord which have been created: \n{log_rec}\n")

    endpoint_response = AskResponse(answer= answer, sources= unique_sources, timing= timing)
    logger.debug(f'Response: {endpoint_response}')
    return endpoint_response

