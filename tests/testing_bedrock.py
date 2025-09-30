# # Use the native inference API to send a text message to Amazon Titan Text G1 - Express.

# import boto3
# import json

# from botocore.exceptions import ClientError

# # Create an Amazon Bedrock Runtime client.
# brt = boto3.client("bedrock-runtime")

# # Set the model ID, e.g., Amazon Titan Text G1 - Express.
# model_id = "eu.anthropic.claude-3-7-sonnet-20250219-v1:0"

# # Define the prompt for the model.
# prompt = "Describe the purpose of a 'hello world' program in one line."

# # Format the request payload using the model's native structure.
# native_request = {
#     "inputText": prompt,
#     "textGenerationConfig": {
#         "maxTokenCount": 512,
#         "temperature": 0.5,
#         "topP": 0.9
#     },
# }

# # Convert the native request to JSON.
# request = json.dumps(native_request)

# try:
#     # Invoke the model with the request.
#     response = brt.invoke_model(modelId=model_id, body=request)

# except (ClientError, Exception) as e:
#     print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
#     exit(1)

# # Decode the response body.
# model_response = json.loads(response["body"].read())

# # Extract and print the response text.
# response_text = model_response["results"][0]["outputText"]
# print(response_text)

# import boto3
# import os

# # Set the API key as an environment variable


# # Create the Bedrock client
# client = boto3.client(
#     service_name="bedrock-runtime",
#     region_name="us-east-1"
# )

# # Define the model and message
# model_id = "eu.anthropic.claude-3-7-sonnet-20250219-v1:0"
# messages = [{"role": "user", "content": [{"text": "Hello! Can you tell me about Amazon Bedrock?"}]}]

# # Make the API call
# response = client.converse(
#     modelId=model_id,
#     messages=messages,
# )

# # Print the response
# print(response['output']['message']['content'][0]['text'])





import sys
import pathlib

cur = pathlib.Path.cwd()
print('cur: ', cur)
sys.path.append(str(cur))

from src import DocumentLoader, Config, Chunker, Indexer, Retriever, LLM, Route

import pprint





# config = Config()
# document_loader = DocumentLoader(config = config)
# files_paths = document_loader.find_files() 

# testing_on_all_files = document_loader.load_files(files = files_paths)

# chunker = Chunker()
# chunks = chunker.documents_to_chunks(testing_on_all_files) # 

# # chunks = [chunk.text for chunk in chunks]
# indexer = Indexer()
# indexer.build_index(chunks)
# print(indexer.query("What is machine learning?"))

# TODO
indexer = Indexer()
index, chunks, model = indexer.load_index()
retriever = Retriever(index = index, chunks = chunks,  model = model)
sources = retriever.retrieve('How do i reinstall printer', k = 5)
# This message comes from the long string when we tokenize it to cut: Token indices sequence length is longer than the specified maximum sequence length for this model (590 > 512). Running this sequence through the model will result in indexing errors


titles = [chunk for chunk, score in sources]
document_titles = ",\n ".join(f'{i+1} {chunk.meta.document_title}' for i, chunk in enumerate(titles))
llm = LLM(route = Route.AWS)
answer = llm.generate(question='What the best league of legends champion?v', sources=titles)
print('-----titles: ----- \n', document_titles)
print('-----LLM answer-----\n', answer)

# to start application with Route.OPENROUTES make sure you have .env file with OPENAI_API_KEY at the directory from which you running the application


# to start application with Route.AWS make sure you have configured and activate appropriate profile with aws cli console at the current directory
# Tips for aws cli: `aws configure list` - see the default profile
# `aws configure list-profiles`  - see which profiles are available
# export AWS_PROFILE=[profilename] - to activate profile which you need, use it without squared brackets

# It's also important to make sure you have model avaialable in your accout, 
# and that this model is available for the region which you configure in the profile or with client (boto3)







# Working configutation from official documentation
# import boto3
# from botocore.exceptions import ClientError

# # Create a Bedrock Runtime client in the AWS Region you want to use.
# client = boto3.client("bedrock-runtime", region_name="eu-north-1")

# # Set the model ID, e.g., Claude 3 Haiku.
# model_id = "eu.anthropic.claude-3-7-sonnet-20250219-v1:0"

# # Start a conversation with the user message.
# user_message = "Describe the purpose of a 'hello world' program in one line."
# conversation = [
#     {
#         "role": "user",
#         "content": [{"text": user_message}],
#     }
# ]

# try:
#     # Send the message to the model, using a basic inference configuration.
#     response = client.converse(
#         modelId=model_id,
#         messages=conversation,
#         inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
#     )

#     # Extract and print the response text.
#     response_text = response["output"]["message"]["content"][0]["text"]
#     print(response_text)

# except (ClientError, Exception) as e:
#     print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
#     exit(1)