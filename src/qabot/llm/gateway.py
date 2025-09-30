import os
import openai
from openai import OpenAI 
from dotenv import load_dotenv
from enum import StrEnum
import boto3


from src.qabot.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.qabot import Retriever, Indexer
from src import Chunk

class Route(StrEnum):
    AWS = "aws"
    OPENROUTES = "openroutes"



class LLM:
    """
    Gateway to the hosted LLM.
    Wraps the provider API and enforces our prompt structure.

    Note: 
        this class depends in .env vatiable  "OPENAI_API_KEY"
    """

    def __init__(self, model: str | None = None, route: Route = Route.OPENROUTES ):
        
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        indexer = Indexer()
        index, chunks, model = indexer.load_index()
        self.retriever = Retriever(index, chunks, model)
        if route is Route.OPENROUTES:
            load_dotenv()
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ["OPENAI_API_KEY"],
            )
            self.route = route
        elif route is Route.AWS:
            # token_aws = os.environ['AWS_BEARER_TOKEN_BEDROCK']
            self.client = boto3.client(    
                service_name="bedrock-runtime",
                region_name="eu-north-1",
                
            )
            self.route = route
        else:
            raise ValueError(f'Provide valid inference provider, possible: {[item.value for item in Route]}')


    def generate(self, question: str, sources: list[Chunk]) -> str | None:
        """
        Generate an answer using the LLM.

        Args:
            question (str): User question.
            sources (list[str]): List of text chunks (retrieved).

        Returns:
            str: Final answer with citations (or "I don’t know").
        """

        system_prompt = SYSTEM_PROMPT
        context = [
            {"text": chunk.text, "path": chunk.meta.path}
            for chunk in sources
        ]
        
        user_prompt = USER_PROMPT_TEMPLATE.format(
            question=question.strip(),
            sources=context,
        )
        if self.route is Route.OPENROUTES:
            complition = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt },
                ],
                max_tokens=500,
                temperature=0.2,
            )
            answer = complition.choices[0].message.content
        elif self.route is Route.AWS:    
            
            model_id = "eu.anthropic.claude-3-7-sonnet-20250219-v1:0"
            messages = [
                    {"role": "user", "content": [{'text': user_prompt}]},
                ]
            system = [{'text': system_prompt}]
            # Make the API call
            response = self.client.converse(
                modelId=model_id,
                messages=messages,
                system = system,
                inferenceConfig={
                    "maxTokens": 500,
                    "temperature": 0.2,
                    }
            )
            
            # Print the response
            answer = response['output']['message']['content'][0]['text']
        else:
            raise ValueError(f'Provide valid inference provider, possible: {[item.value for item in Route]}')
        

        return  answer