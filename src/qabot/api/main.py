import time
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from .schemas import Turn, AskRequest
from src import Indexer,Retriever,LLM, Route, USER_PROMPT_TEMPLATE, SYSTEM_PROMPT, get_custom_logger 
from src.qabot.api.routers.health import health_router
from src.qabot.api.routers.ask import ask_router
logger= get_custom_logger(log_file='main')

@asynccontextmanager
async def lifespan(app: FastAPI):
    indexer = Indexer()
    index, chunks, model = indexer.load_index()
    app.state.retriever = Retriever(index=index,chunks=chunks,model=model)
    app.state.llm = LLM(route=Route.AWS)
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG_QA_bot",
        version="0.1.0",
        description="FastAPI service for Retrieval-Augumented Generator LLM calling.",
        lifespan = lifespan
    )
    app.include_router(health_router)
    app.include_router(ask_router)
    return app

app = FastAPI(lifespan=lifespan)

@app.get('/health')
async def helath():
    return {'status':'ok'}

@app.post('/ask')
async def ask(reqest: Request, payload: AskRequest):
    perf_total_start = time.perf_counter()

    perf_retrieve_start = time.perf_counter()
    question=payload.question.strip()
    retrieved = app.state.retriever.retrieve(question, k=5)
    perf_retrieve_end = time.perf_counter()

    perf_llm_start = time.perf_counter()
    prompt_sources = [{"text": chunk.text, "path": chunk.meta.path} for chunk, i in retrieved]
    user_prompt = USER_PROMPT_TEMPLATE.format(question=question, sources=prompt_sources)
    #perf_llm_start = time.perf_counter()
    answer = app.state.llm.generate(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)
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
    timing={
    'retrieve_ms': int( (perf_retrieve_end - perf_retrieve_start) * 1000 ),
    'llm_ms': int( (perf_llm_end - perf_llm_start ) * 1000),
    'total_ms': int((perf_total_end - perf_total_start ) * 1000)
    }
    endpoint_response = {'answer': answer, 'sources': unique_sources, 'timing': timing}
    return endpoint_response

# returns {answer, sources, timings}


# {
#   "answer": "…5–7 line Markdown…\n\nSources:\n- equipment.md …",
#   "sources": [
#     {"title": "equipment", "path": "data/tinyco/equipment.md", "updated_at": "2025-08-25"}
#   ],
#   "timings": {"retrieve_ms": 80, "llm_ms": 1400, "total_ms": 1580}
# }
    

#     logger.info(f"Retrieved documents")
#     logger.info(f'Recieved User Question, user question: {question}')
