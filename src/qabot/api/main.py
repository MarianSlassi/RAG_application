from fastapi import FastAPI
from contextlib import asynccontextmanager
import sqlite3

from transformers import AutoTokenizer

from src.qabot.indexer import Indexer
from src.qabot.search import Retriever
from src.qabot.llm.gateway import LLM, Route
from src.qabot.helpers.logger import get_custom_logger 
from src.qabot.api.routers.health import health_router
from src.qabot.api.routers.ask import ask_router
from src.qabot.api.routers.summarize import summarize_router
from src.qabot.helpers.config import Config
from src.qabot.helpers.project_config import load_project_config
from src.qabot.search.reranker import Reranker
from src.qabot.repository.log_repository import LogRepository

logger= get_custom_logger(log_file='main')
@asynccontextmanager
async def lifespan(app: FastAPI):
    config = Config()
    indexer = Indexer()
    index, chunks, model, bm25, tokenized_corpus_bm25 = indexer.load_index()
    app.state.retriever = Retriever(index=index, chunks=chunks, model=model,
                                     index_bm25=bm25, tokenized_corpus_bm25=tokenized_corpus_bm25)
    app.state.reranker = Reranker(model_name="BAAI/bge-reranker-base", use_fp16=True, device=None, batch_size=16)
    app.state.llm = LLM(route=Route.OPENROUTES)
    app.state.project_config = load_project_config()
    app.state.tokenizer =  AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
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

