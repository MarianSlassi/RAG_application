from fastapi import Request

def get_retriever(request: Request):
    return request.app.state.retriever

def get_llm(request: Request):
    return request.app.state.llm