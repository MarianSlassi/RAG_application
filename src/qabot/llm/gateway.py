import os
from openai import OpenAI 
from dotenv import load_dotenv
from enum import StrEnum
import boto3
from typing import Any


from src.qabot.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.qabot import Retriever, Indexer
from src.qabot.schemas import Chunk
from src.qabot.helpers import load_project_config

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

    def __init__(self, project_config: dict[str, Any] | None = None, route: Route = Route.OPENROUTES):
        '''
        Initiate LLM state  as a client with a given Route. 
        Depends on:
            Environment variables:
                os.environ["OPENAI_API_KEY"]
            Project Config variables:
                ['llm']['openai']['client']['base_url']
                ['llm']['aws']['client']['service_name']
                ['llm']['aws']['client']['region_name']

        '''
        self.config = project_config or load_project_config() 

        if route is Route.OPENROUTES:
            load_dotenv()
            self.client = OpenAI(
                base_url=self.config['llm']['openai']['client']['base_url'],
                api_key=os.environ["OPENAI_API_KEY"],
            )
            self.route = route
        elif route is Route.AWS:
            # token_aws = os.environ['AWS_BEARER_TOKEN_BEDROCK']
            self.client = boto3.client(    
                service_name=self.config['llm']['aws']['client']['service_name'],
                region_name=self.config['llm']['aws']['client']['region_name'],
                
            )
            self.route = route
        else:
            raise ValueError(f'Provide valid inference provider, possible: {[item.value for item in Route]}')


    def generate(self, system_prompt, user_prompt ) -> str | None:
        """
        Generate an answer using the LLM.

        Args:
            system_prompt (str)
            user_prompt (str)

        Returns:
            str: Final answer with citations (or "I don’t know").
        Depends on:
            Variables from other project files:
                SYSTEM_PROMPT,USER_PROMPT_TEMPLATE
            Project Config variables:
                ['llm']['openai']['model_settings']['model']
                ['llm']['openai']['model_settings']['max_tokens']
                ['llm']['openai']['model_settings']['temperature']
                ['llm']['aws']['model_settings']['model_id']
                ['llm']['aws']['model_settings']["max_tokens"]
                ['llm']['aws']['model_settings']["temperature"]

        """
        if self.route is Route.OPENROUTES:
            complition = self.client.chat.completions.create(
                model=self.config['llm']['openai']['model_settings']['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt },
                ],
                max_tokens=self.config['llm']['openai']['model_settings']['max_tokens'],
                temperature=self.config['llm']['openai']['model_settings']['temperature'],
            )
            answer = complition.choices[0].message.content
        elif self.route is Route.AWS:    
            messages = [
                    {"role": "user", "content": [{'text': user_prompt}]},
                ]
            system = [{'text': system_prompt}]
            response = self.client.converse(
                modelId=self.config['llm']['aws']['model_settings']['model_id'],
                messages=messages,
                system = system,
                inferenceConfig={
                    'maxTokens': self.config['llm']['aws']['model_settings']["max_tokens"],
                    'temperature':self.config['llm']['aws']['model_settings']["temperature"],
                    }
            )
            answer = response['output']['message']['content'][0]['text']
        else:
            raise ValueError(f'Provide valid inference provider, possible: {[item.value for item in Route]}')
        

        return  answer