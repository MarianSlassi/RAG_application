# Project of Building basic RAG-app

In this project we build simple chat-RAG </br>
Data is taken from there: https://www.kaggle.com/datasets/dkhundley/synthetic-it-related-knowledge-items
# Classes
Navigate to root/docs to get info about classes used in the project, the short list:
- Config() - as custom helper, used to store paths to data files
- DocumentLoader()
- Chunker()
- Indexer()
- Retriever()
- LLM()
# Tests
Since src/ and tests/ are neighboring subfolders, run tests from project root with:
- `python -m pytest tests/test_loader.py`
- `python -m pytest tests/test_chunker.py`
# Dependencies when Running LLM()
### Routers
to start application with Route.OPENROUTES make sure you have .env file with OPENAI_API_KEY at the directory from which you running the application
to start application with Route.AWS make sure you have configured and activate appropriate profile with aws cli console at the current directory
Tips for aws cli: `aws configure list` - see the default profile
`aws configure list-profiles`  - see which profiles are available
export AWS_PROFILE=[profilename] - to activate profile which you need, use it without squared brackets
It's also important to make sure you have model avaialable in your accout, 
and that this model is available for the region which you configure in the profile or with client (boto3)
# Schemas
# Other
Other possible solution is to use our modul as package, will need additional setup rather than following but :
[tool.setuptools]
packages = ["src"]
