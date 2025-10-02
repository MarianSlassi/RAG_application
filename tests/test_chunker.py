import sys
sys.path.append('../src')

from datetime import date

import pytest

from src import Chunker
from src import Document



class DummyTokenizer:
    def __init__(self, model_max_length: int = 64) -> None:
        self.model_max_length = model_max_length

    def encode(self, text: str) -> list[str]:
        return self.tokenize(text)

    def tokenize(self, text: str) -> list[str]:
        return [token for token in text.split() if token]

    def convert_tokens_to_string(self, tokens: list[str]) -> str:
        return " ".join(tokens)


@pytest.fixture
def tokenizer() -> DummyTokenizer:
    return DummyTokenizer(model_max_length=64)


@pytest.fixture
def chunker(tokenizer: DummyTokenizer) -> Chunker:
    return Chunker(tokenizer=tokenizer)


@pytest.fixture
def sample_document() -> Document:
    return Document(
        title="sample-doc",
        path="data/docs/sample.md",
        filetype="md",
        updated_at=date(2024, 1, 1),
        text=(
            "Intro paragraph for the document"
            "\n\n**Overview**\n\n"
            "Overview content with some words"
            "\n\n**Details**\n\n"
            "Deeper insight provided here"
        ),
    )


def test_split_text_splits_markdown_sections(chunker: Chunker, sample_document: Document) -> None:
    parts = chunker._split_text(sample_document)

    assert [part.strip() for part in parts] == [
        "Intro paragraph for the document",
        "Overview content with some words",
        "Deeper insight provided here",
    ]


def test_process_split_text_merges_short_fragments(chunker: Chunker) -> None:
    fragments = [
        "This chunk already has enough tokens to stay separate",
        "Tiny fragment",
        "Small bit",
    ]

    processed = chunker._process_split_text(fragments, min_tokens=3)

    assert len(processed) == 2
    assert processed[0].startswith("This chunk already has enough tokens")
    assert "Tiny fragment" in processed[1]
    assert "Small bit" in processed[1]


def test_documents_to_chunks_creates_expected_meta(
    chunker: Chunker, sample_document: Document
) -> None:
    chunks = chunker.documents_to_chunks([sample_document], min_tokens=2)

    assert len(chunks) == 3
    assert [chunk.text.strip() for chunk in chunks] == [
        "Intro paragraph for the document",
        "Overview content with some words",
        "Deeper insight provided here",
    ]

    first = chunks[0]
    assert first.id == "sample-doc_0"
    assert first.meta.document_title == sample_document.title
    assert first.meta.path == sample_document.path
    assert first.meta.section_id == 0
    assert first.meta.section_title == ""
    assert first.meta.tokens == len(chunker.tokenizer.encode(first.text))
    assert first.meta.updated_at == sample_document.updated_at


def test_documents_to_chunks_rejects_min_tokens_not_less_than_context(
    chunker: Chunker, sample_document: Document
) -> None:
    with pytest.raises(ValueError):
        chunker.documents_to_chunks([sample_document], min_tokens=chunker.context_window)
