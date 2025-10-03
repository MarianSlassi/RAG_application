import time
from fastapi import FastAPI
from contextlib import asynccontextmanager


from src import Indexer,Retriever,LLM, Route, USER_PROMPT_TEMPLATE, SYSTEM_PROMPT, get_custom_logger 
from src.qabot.api.routers.health import health_router
from src.qabot.api.routers.ask import ask_router
from src.qabot.api.routers.summarize import summarize_router
logger= get_custom_logger(log_file='main')

@asynccontextmanager
async def lifespan(app: FastAPI):
    indexer = Indexer()
    index, chunks, model = indexer.load_index()
    app.state.retriever = Retriever(index=index,chunks=chunks,model=model)
    app.state.llm = LLM(route=Route.AWS)
    yield

def create_app(lifespan) -> FastAPI:
    app = FastAPI(
        title="RAG_QA_bot",
        version="0.1.0",
        description="FastAPI service for Retrieval-Augumented Generator LLM calling.",
        lifespan = lifespan
    )
    app.include_router(health_router)
    app.include_router(ask_router)
    app.include_router(summarize_router)
    return app

app = create_app(lifespan=lifespan)

