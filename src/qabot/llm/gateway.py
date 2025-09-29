import os
import openai
from openai import OpenAI  # можно заменить на любой LLM-провайдер
from dotenv import load_dotenv

from src.qabot.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.qabot import Retriever, Indexer
from src import Chunk


class LLM:
    """
    Gateway to the hosted LLM.
    Wraps the provider API and enforces our prompt structure.
    """

    def __init__(self, model: str | None = None):
        load_dotenv()
        # модель берём из аргумента или переменной окружения
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        indexer = Indexer()
        index, chunks, model = indexer.load_index()
        self.retriever = Retriever(index, chunks, model)
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENAI_API_KEY"],
        )       

    def generate(self, question: str, sources: list[Chunk]) -> str | None:
        """
        Generate an answer using the LLM.

        Args:
            question (str): User question.
            sources (list[str]): List of text chunks (retrieved).

        Returns:
            str: Final answer with citations (or "I don’t know").
        """
        # Берём только 2–3 чанка
        context = [chunk.text for chunk in sources]
        #context = "\n\n".join(sources[:3]) if sources else "No sources found."

        user_prompt = USER_PROMPT_TEMPLATE.format(
            question=question.strip(),
            sources=context,
        )

        document_titles = ",\n ".join(f'{i+1} {chunk.meta.document_title}' for i, chunk in enumerate(sources))
        
        system_prompt = SYSTEM_PROMPT.format(document_titles=document_titles)
        # Вызов API
        complition = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
            temperature=0.2,
        )
        answer = complition.choices[0].message.content
        return  answer
        # return resp["choices"][0]["message"]["content"].strip()