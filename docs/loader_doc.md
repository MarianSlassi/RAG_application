# DocumentLoader

`DocumentLoader` (`src/qabot/ingest/loader.py`) walks a directory tree, extracts plain text from Markdown/PDF/Word files, and returns a list of `Document` objects populated with metadata. It feeds the `Chunker` in the ingestion pipeline.

## Dependencies
- `src.helpers.Config` – provides the canonical content root via `config.get('canonical_dir')`.
- `src.schemas.Document` – Pydantic schema the loader must populate (`title`, `path`, `filetype`, `updated_at`, `text`).
- `PyPDF2.PdfReader` – parses PDF files page by page.
- `python-docx.Document` – reads Microsoft Word `.docx` paragraphs.
- Standard library: `os`, `datetime` – filesystem traversal, timestamps, and fallback metadata.

## Flow Overview
```
[Filesystem]
    |
    v
find_files
    |
    v
load_files
    |
    v
_parse_file
    |
    v
_extract_text
    |
    v
[Document]
```

- `load_files` is the entry point that orchestrates discovery and parsing.
- `find_files` gathers absolute file paths under the configured root, filtered by extension.
- `_parse_file` enriches raw text with metadata (`title`, `filetype`, `updated_at`).
- `_extract_text` is format-specific text extraction (Markdown, PDF, DOCX).

## Public API

### `DocumentLoader(config: Config)`
Accepts a `Config` instance (defaults to the project-wide `Config`). The loader reads `canonical_dir` when callers omit an explicit search path.

### `find_files(path: str | None = None, allowed_ext: tuple[str, ...] = ('.md', '.pdf', '.docx')) -> list[str]`
Recursively traverses `path` (or `config.get('canonical_dir')` if `None`) and returns absolute paths for files whose suffix matches `allowed_ext`. Raises `ValueError` when the provided `path` is not a directory or when no canonical directory is configured.

### `load_files(files: list[str] | None = None) -> list[Document]`
Builds `Document` instances. If `files` is `None`, it calls `find_files()` first; otherwise it trusts the provided list. For each path it delegates to `_parse_file` and accumulates the results.

## Internal Helpers
- `_extract_text(file: str) -> str`  
  Dispatches by file extension. PDFs are read via `PdfReader`, DOCX files via `python-docx`, and Markdown/other text files via UTF-8 `open()`.

- `_parse_file(file: str) -> Document`  
  Calls `_extract_text`, derives `title` from the basename, captures `filetype` from the extension, and searches the text for a leading `updated:` line (`YYYY-MM-DD`). If missing, it falls back to the filesystem mtime (`datetime.date`).

## Data Drift Watchpoints (inside `load_files`)
- **Extension drift** – Adding new source formats (e.g., HTML, CSV) will be skipped because `allowed_ext` defaults to Markdown/PDF/DOCX. Update the tuple and extend `_extract_text` as formats change.
- **Metadata drift** – `_parse_file` expects the `updated:` marker in ISO format. Deviations (`Updated on`, different delimiters) cause it to rely on filesystem timestamps. Monitor this to avoid stale dates.
- **Encoding drift** – Plain-text files are opened as UTF-8. If upstream documents switch encoding, decoding errors or mojibake will slip into `text`.

## Example Usage

```python
from src.qabot.ingest.loader import DocumentLoader
from src.helpers import Config

config = Config()
loader = DocumentLoader(config=config)
documents = loader.load_files()  # internally calls find_files()
```

`documents` is a list of `Document` models ready for chunking or downstream processing.
