import os
import time
import json
from typing import Any
from enum import StrEnum
from dotenv import load_dotenv
from openai import OpenAI
import boto3
import botocore

from src.qabot.helpers import load_project_config
from src.qabot.helpers.logger import get_custom_logger

logger = get_custom_logger(__name__)

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


    def generate(self, system_prompt, user_prompt, structured: bool = False, schema: dict | None = None ) -> dict[str, Any]:
        """
        Generate an answer using the LLM. 

        Args:
            system_prompt (str): System-level instruction.
            user_prompt (str): User's query.
            structured (bool): If True, expect JSON as output object (parsed to dict) in response.

        Returns:
            str | dict: String response or structured JSON object.
        """
        
        if self.route is Route.OPENROUTES:
            answer = self._generate_openai(system_prompt=system_prompt, user_prompt=user_prompt, structured=structured, schema=schema)
        elif self.route is Route.AWS:
            if structured:
                raise ValueError("Using structured output isn't possible with AWS in current version")
            answer = self._generate_aws(system_prompt=system_prompt, user_prompt=user_prompt)
        else:
            raise ValueError(f'Provide valid inference provider, possible: {[item.value for item in Route]}')
        return answer
    def _generate_openai(self, system_prompt, user_prompt, structured: bool = False, schema: dict | None = None):
        """
        Depends on:
            Project Config variables:
                ['llm']['openai']['model_settings']['model']
                ['llm']['openai']['model_settings']['max_tokens']
                ['llm']['openai']['model_settings']['temperature']
        """
        kwargs = dict(
            model=self.config['llm']['openai']['model_settings']['model'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self.config['llm']['openai']['model_settings']['max_tokens'],
            temperature=self.config['llm']['openai']['model_settings']['temperature'],
            )
        if structured:
            kwargs["response_format"] = {"type": "json_object"}
            if schema:
                kwargs["response_format"] = schema

        completion = self.client.chat.completions.create(**kwargs)
        content = completion.choices[0].message.content
        logger.debug(f'completion : \n {completion}\n')
        if structured:
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON from LLM: {e}\nContent: {content}")
                return {"error": "Invalid JSON from model", "raw_content": content}
            
        return content
    def _generate_aws(self, system_prompt, user_prompt):
        """
        Depends on:
            Project Config variables:
                ['llm']['aws']['model_settings']['model_id']
                ['llm']['aws']['model_settings']["max_tokens"]
                ['llm']['aws']['model_settings']["temperature"]
        """
        messages = [
                {"role": "user", "content": [{'text': user_prompt}]},
            ]
        system = [{'text': system_prompt}]

        max_attempts=self.config['llm']['retry_on_throttling']['max_attempts']
        base_delay = self.config['llm']['retry_on_throttling']['base_delay']
        for attempt in range(max_attempts):
            try:
                response = self.client.converse(
                    modelId=self.config['llm']['aws']['model_settings']['model_id'],
                    messages=messages,
                    system = system,
                    inferenceConfig={
                        'maxTokens': self.config['llm']['aws']['model_settings']["max_tokens"],
                        'temperature':self.config['llm']['aws']['model_settings']["temperature"],
                        }
                )  
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "ThrottlingException":
                    wait = base_delay ** attempt
                    logger.warning(f"Rate limit hit, retrying in {wait}s (attempt {attempt + 1}/{max_attempts})...")
                    time.sleep(wait)
                else:
                    raise
            
        return response['output']['message']['content'][0]['text']
    # TODO: integrate retry as decorator also for Route.OPENROUTES - not integrated yet, cause clinet calling better to cope into independent class  
    