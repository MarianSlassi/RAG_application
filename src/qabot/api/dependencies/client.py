from fastapi import Request, Depends

def get_retriever(request: Request):
    return request.app.state.retriever

def get_llm(request: Request):
    return request.app.state.llm