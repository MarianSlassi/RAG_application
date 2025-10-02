import sys
import pathlib

cur = pathlib.Path.cwd()
print('cur: ', cur)
sys.path.append(str(cur))

from src import DocumentLoader, Config, Chunker, Indexer, Retriever, LLM, Route, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE



indexer = Indexer()
index, chunks, model = indexer.load_index()
retriever = Retriever(index = index, chunks = chunks,  model = model)
llm = LLM(route = Route.AWS)

def ask_model(question:str, llm, retriever):
    print('-'*20)
    sources = retriever.retrieve(question, k = 5)
    system_prompt = SYSTEM_PROMPT
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

ask_model(question= 'How do i install a printer?', llm = llm, retriever=retriever)
