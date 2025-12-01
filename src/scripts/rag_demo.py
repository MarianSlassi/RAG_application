import sys
import pathlib

cur = pathlib.Path.cwd()
print('cur: ', cur)
sys.path.append(str(cur))

from src.qabot import Indexer
from src.qabot.search.retriever import Retriever
from src.qabot.llm.gateway import LLM, Route
from src.qabot.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.qabot.search.reranker import Reranker

indexer = Indexer()
index, chunks, model, bm25, tokenized_corpus_bm25 = indexer.load_index()
retriever = Retriever(index=index, chunks=chunks,  model=model, index_bm25=bm25, tokenized_corpus_bm25=tokenized_corpus_bm25)
llm = LLM(route = Route.OPENROUTES)
reranker = Reranker()

def ask_model(question:str, llm, retriever, k, bm_25:bool=False):
    """
    This script used to show the RAG POC version
    """
    print('-'*20)
    sources = retriever.retrieve(question, k=k, normalize=True)
    sources_bm25 = retriever.bm25_retrieve(question, k=k, normalize=True)
    hybrid_sources = retriever.hybrid_retrieve(question, k=k)
    
    hybrid_chunks = [chunk for chunk, _ in hybrid_sources]
    reranked_sources = reranker.rerank(query=question, chunks=hybrid_chunks, top_k=k)

    system_prompt = SYSTEM_PROMPT
    if bm_25:
        context = [
        {"text": chunk.text, "path": chunk.meta.path}
        for chunk, score in sources_bm25
        ]
    else:
        context = [
        {"text": chunk.text, "path": chunk.meta.path}
        for chunk, score in sources
        ]

    user_prompt = USER_PROMPT_TEMPLATE.format(
        question=question.strip(),
        sources=context,
    )
    print('User question: ', question)

    # This message comes from the long string when we tokenize it to cut: Token indices sequence length is longer than the specified maximum sequence length for this model (590 > 512). Running this sequence through the model will result in indexing errors
    titles = [chunk for chunk, score in sources]
    document_titles = ",\n ".join(f'{i+1} {chunk.meta.document_title}' for i, chunk in enumerate(titles))
    answer = llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)
    print('-----retrieved documents: ----- \n', document_titles)
    print('-----LLM answer-----\n', answer)
    print('-'*20)

ask_model(question= 'How do i install a printer?', llm = llm, retriever=retriever, k=6,  bm_25= False)
