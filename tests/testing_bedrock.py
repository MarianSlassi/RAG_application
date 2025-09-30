import sys
import pathlib

cur = pathlib.Path.cwd()
print('cur: ', cur)
sys.path.append(str(cur))

from src import DocumentLoader, Config, Chunker, Indexer, Retriever, LLM, Route



indexer = Indexer()
index, chunks, model = indexer.load_index()
retriever = Retriever(index = index, chunks = chunks,  model = model)
llm = LLM(route = Route.AWS)




def question_answer(question:str):
    print('-'*20)
    sources = retriever.retrieve(question, k = 5)
    print('User question: ', question)

    # This message comes from the long string when we tokenize it to cut: Token indices sequence length is longer than the specified maximum sequence length for this model (590 > 512). Running this sequence through the model will result in indexing errors
    titles = [chunk for chunk, score in sources]
    document_titles = ",\n ".join(f'{i+1} {chunk.meta.document_title}' for i, chunk in enumerate(titles))
    answer = llm.generate(question=question, sources=titles)
    print('-----retrieved documents: ----- \n', document_titles)
    print('-----LLM answer-----\n', answer)
    print('-'*20)

question_answer(question= 'What is the best hero in league of legends?')
