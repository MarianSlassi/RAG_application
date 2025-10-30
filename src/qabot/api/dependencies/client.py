from fastapi import Request
import sqlite3
from src.qabot.helpers.config import Config
from src.qabot.repository.log_repository import LogRepository, Database

def get_retriever(request: Request):
    return request.app.state.retriever

def get_llm(request: Request):
    return request.app.state.llm

def get_db_connection():
    config = Config()
    with Database._connect(config['logs_db']) as conn:
        yield conn

def get_project_config(requests: Request):
    return requests.app.state.project_config