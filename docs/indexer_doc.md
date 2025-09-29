# Indexer

`Indexer` (`src/qabot/indexer.py`) encodes text chunks, builds a FAISS similarity index, and persists both the index and the chunk payloads. It sits after `Chunker` and before any retrieval or Q&A component.

## Dependencies
- `src.helpers.Config` – supplies filesystem locations for `index_file` and `chunks_file`.
- `sentence_transformers.SentenceTransformer` – turns text into L2-normalized embeddings (defaults to `sentence-transformers/all-MiniLM-L6-v2`).
- `faiss` – stores embeddings in an inner-product index and performs nearest-neighbour search.
- `numpy` – holds the dense embedding matrix.
- `pickle` – serializes chunk text so that retrieved IDs can map back to content.

# ⚠️ Config dependincies inside:
- Uses `config['chunks_file]` and `config['index_file]`

## Flow Overview

1. **Chunks In** → `build_index`  
   - encode with `SentenceTransformer`  
   - add vectors to `faiss.IndexFlatIP`  
   - persist `index.faiss` and `chunks.pkl`
2. **Query Text** → `query`  
   - lazy-load via `load_index` if needed  
   - encode query, search FAISS  
   - return `(chunk_text, score)` pairs


## Public API

### `Indexer(config: Config | None = None, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2')`
Accepts an optional `Config` and embedding model name. When `config` is omitted, a fresh `Config()` is created, ensuring the index directory exists.

### `build_index(chunks: list[str]) -> None`
Encodes each chunk with the configured transformer, builds an inner-product FAISS index, writes it to `config['index_file']`, and pickles the raw chunk texts to `config['chunks_file']`. Also caches the index, chunk list, and model inside the instance for reuse.

### `load_index() -> tuple[faiss.Index, list[str], SentenceTransformer]`
Lazy loads the serialized index and chunk payloads. Returns cached objects if already present; otherwise reads from disk and instantiates a fresh transformer using `model_name`.

### `query(text: str, k: int = 3) -> list[tuple[str, float]]`
Embeds the query text, searches the FAISS index for the top-`k` matches, and returns `(chunk_text, similarity_score)` tuples sorted by score.

## Internal State
- `_index` – the in-memory FAISS index for reuse across queries.
- `_chunks` – the ordered list of chunk texts; aligns with the embedding matrix.
- `_model` – cached transformer to avoid repeated instantiation during interactive use.


## Example Usage

```python
from src.helpers.config import Config
from src.qabot.ingest.loader import DocumentLoader
from src.qabot.ingest.chunker import Chunker
from src.qabot.indexer import Indexer

config = Config()

document_loader = DocumentLoader(config=config)
files_paths = document_loader.find_files()
testing_on_all_files = document_loader.load_files(files=files_paths)

chunker = Chunker()
chunks = chunker.documents_to_chunks(testing_on_all_files)

chunks = [chunk.text for chunk in chunks]

indexer = Indexer(config=config)
indexer.build_index(chunks)

print(indexer.query("What is machine learning?"))
query returns a list of (chunk_text, score) pairs ordered by similarity to the prompt.

```

