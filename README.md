# Project of Building basic RAG-app

In this project we build simple chat-RAG </br>
Data is taken from there: https://www.kaggle.com/datasets/dkhundley/synthetic-it-related-knowledge-items
# Classes
Navigate to root/docs to get info about classes used in the project, the short list:
- Config() - as custom helper, used to store paths to data files
- DocumentLoader()
- Chunker()
- Indexer()
# Tests
Run tests from project root with `python -m pytest tests/test_chunker.py`since src/ and tests/ are neighboring subfolders.
Other possible solution is to use our modul as package, will need additional setup rather than following but :
[tool.setuptools]
packages = ["src"]