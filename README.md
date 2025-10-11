# Project of Building basic RAG-app

In this project we build simple chat-RAG </br>
Data is taken from there: https://www.kaggle.com/datasets/dkhundley/synthetic-it-related-knowledge-items
# Notes
 - Note that project has two configs, one for data and files path (Config class), and the second for all other project constants - project_config.yaml
# Classes
Navigate to root/docs to get info about classes used in the project, the short list:
- Config() - as custom helper, used to store paths to data files
- DocumentLoader()
- Chunker()
- Indexer()
- Retriever()
- LLM()
# Functions
- load_project_config() - project config which stores constant varialbes for example: tempretature for model from a specific provider
# Variables
- SYSTEM_PROMPT - used as default system prompt for every call to model from a specific provider
- USER_PROMPT_TEMPLATE - used as default user prompt for every call to model from a specific provider
# .env variables
- OPENAI_API_KEY - api key for calling opean ai model from OpenAI SDK
# Tests
Since src/ and tests/ are neighboring subfolders, run tests from project root with:
- `python -m pytest tests/test_loader.py`
- `python -m pytest tests/test_chunker.py`
# Scripts
`uv run python -m src.scripts.docs_2_chunks` - to chunk documents and save it with index
`uv run -m src.qabot.evals.eval` - to evaluate a model

# Running LLM() class
## Routers
### Route.OPENROUTES
To start application with Route.OPENROUTES make sure you have .env file with OPENAI_API_KEY at the directory from which you running the application
### Route.AWS
To start application with Route.AWS make sure you have configured and activate appropriate profile with aws cli console at the current directory
</br>Tips for aws cli: 
    </br>`aws configure list` - see the default profile
    </br>`aws configure list-profiles`  - see which profiles are available
    </br>`export AWS_PROFILE=[profilename]` - to activate profile which you need, use it without squared brackets
It's also important to make sure you have model avaialable in your accout, 
and that this model is available for the region which you configure in the profile or with client (boto3)

# Web API
## Running
### Backend
Original: `uv run uvicorn src.qabot.api.main:app`</br>
### Front
`uv run python -m streamlit run src/qabot/web/app.py`
# Schemas
# Other

