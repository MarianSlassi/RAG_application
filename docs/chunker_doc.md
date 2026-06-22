# Chunker

`Chunker` (`src/qabot/ingest/chunker.py`) transforms a list of `Document` instances into `Chunk` objects that carry plain text plus structured metadata (`Meta`). It sits directly after `DocumentLoader` in the ingestion pipeline.

## Dependencies
- `transformers.AutoTokenizer` – token counting, splitting on the model’s context window (defaults to `sentence-transformers/all-MiniLM-L6-v2`).
- `src.schemas.Document` – input schema defined elsewhere in the project.
- `src.schemas.chunk.{Chunk, Meta}` – output schemas that enforce ID layout, token limits, and metadata fields.

## Flow Overview
```
[Documents]
    |
    v
_split_text
    |
    v
_process_split_text
    |--> _cut_long_text
    |--> _merge_short_text
    |
    v
documents_to_chunks
    |
    v
[Chunks]
```

- `documents_to_chunks` drives the full conversion.
- `_split_text` slices document bodies at Markdown headings (`\n**Heading**\n`).
- `_process_split_text` normalizes fragment size by cutting long segments and merging undersized ones.
- `Chunk` instances receive consistent IDs, token counts, and metadata such as source path and document title.

## Public API

### `Chunker(tokenizer=None)`
Initializes the helper tokenizer; if none is provided, loads `sentence-transformers/all-MiniLM-L6-v2` and stores its `model_max_length` as the context window.

### `documents_to_chunks(documents: list[Document], min_tokens: int=150) -> list[Chunk]`
Main entry point. For each document:
1. Pulls `title` and `path`.
2. Calls `_split_text` followed by `_process_split_text`.
3. Iterates over normalized fragments, assigning `section_id`, counting tokens, and building `Chunk` objects with `Meta`.

IDs follow the pattern `<document_title>_<section_id>`; token counts must remain within the tokenizer’s maximum length.

## Internal Helpers

- `_count_tokens(text: str) -> int`  
  Encodes text with the configured tokenizer; raises if no tokenizer is available.

- `_split_text(document: Document) -> list[str]`  
  Regex-based split on Markdown-style bold headings. Returns raw text fragments without metadata.

- `_cut_long_text(text: str, overlap_percent: float = 0.10) -> list[str]`  
  Tokenizes the string, emits overlapping slices whenever the token count exceeds `context_window`. Overlap defaults to 10%.

- `_merge_short_text(sequences: list[str]) -> list[str]`  
  Greedily merges fragments shorter than ~150 tokens with neighbors while respecting the context window.

- `_process_split_text(sequence: list[str], min_tokens=150) -> list[str]`  
  Applies `_cut_long_text` to each fragment, then `_merge_short_text` to smooth out short segments; returns normalized text pieces.

## Data Drift Watchpoints (inside `documents_to_chunks`)
- **Format drift** – `_split_text` assumes headings look like `\n**Title**\n`. If new documents change heading syntax (e.g., `# Heading`, HTML tags, or no headings), chunk boundaries fail. Monitor heading extraction rates or fallback to heuristic chunk sizes.
- **Length drift** – `_cut_long_text` and `_merge_short_text` tune chunk lengths around the tokenizer window and a hard-coded 150-token minimum. A sudden shift toward very long or very short documents may require adjusting overlap or minimum thresholds.
- **Tokenizer drift** – The default MiniLM tokenizer handles English best; if documents trend toward other languages or mixed scripts, token counts and context adherence may deviate. Consider re-tokenizing with a multilingual model when such drift is detected.

## Example Usage

```python
from src.qabot.ingest.chunker import Chunker
from src.qabot.ingest.loader import DocumentLoader
from src.helpers import Config

config = Config()
documents = DocumentLoader(config).load_files()
chunker = Chunker()
chunks = chunker.documents_to_chunks(documents)
```

`chunks` is a list of `Chunk` objects ready for embedding, storage, or retrieval.


