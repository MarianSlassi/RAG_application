# Project of Building basic RAG-app

In this project we build simple chat-RAG </br>
Data is taken from there: https://www.kaggle.com/datasets/dkhundley/synthetic-it-related-knowledge-items

# Classes
## DocumentLoader()
1. Initilize every instance with Config object
2. When use `find_files(path:str)` by default uses `self.config.get('canonical_dir')` dir

</br>
</br>
Instance of usage:

```
from src.qabot.ingest import DocumentLoader
from src.helpers import Config

config = Config()
document_loader = DocumentLoader(config=config)
files = document_loader.find_files()

files_list = document_loader._load_files(files = files)
```
List of methods (private and public):
```
Public methods
--------------
find_files(path: str | None = None,
           allowed_ext: tuple = ('.md', '.pdf', '.docx')) -> list[str]
    Recursively scans *path* (or the canonical directory from Config if none
    given) and returns absolute paths of all files whose extensions match
    `allowed_ext`.

load_files(files: list[str] | None = None) -> list[Document]
    High-level loader. For each path in *files* (or from `find_files()` if
    none provided), calls `_parse_file()` and assembles a list of Document
    instances.

Private methods
---------------
_extract_text(file: str) -> str
    Reads the content of a single file and extracts plain text.
    Supports .md (UTF-8 text), .pdf (via PyPDF2), and .docx (via python-docx).

_parse_file(file: str) -> Document
    Uses `_extract_text()` to get the file’s full text, then
    derives metadata:
      • `title` – files' name.
      • `updated_at` – first line starting with `updated:` or fallback to files' metaingormation.
    Returns a `Document` Pydantic object.


```

ASCII Overview:
```
          ┌───────────┐
          │find_files │─────┐   (get list of file paths)
          └─────┬─────┘     │
                ▼           │
          ┌───────────┐     │
          │_load_files│◄────┘   (entry point to build list[Document])
          └─────┬─────┘
                ▼
          ┌───────────┐
          │_parse_file│   (extract metadata + text for one file)
          └─────┬─────┘
                ▼
          ┌─────────────┐
          │_extract_text│   (low-level text extraction)
          └─────────────┘
```
## Config()