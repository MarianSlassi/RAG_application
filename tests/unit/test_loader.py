import os
import tempfile
from datetime import date
import pytest

from src import Config
from src import Document
from src import DocumentLoader

# Note that tmp_path is embedded (default) pytest fixture

def test_find_files_returns_files(tmp_path):
    f = tmp_path / "sample.md"
    f.write_text("some text")

    loader = DocumentLoader(config=Config())
    files = loader.find_files(path=str(tmp_path))
    assert len(files) == 1
    assert files[0].endswith("sample.md")


def test_extract_text_md(tmp_path):
    f = tmp_path / "file.md"
    f.write_text("hello world")
    loader = DocumentLoader(config=Config())
    text = loader._extract_text(str(f))
    assert "hello world" in text


def test_parse_file_md(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("simple content")
    loader = DocumentLoader(config=Config())
    doc = loader._parse_file(str(f))
    assert isinstance(doc, Document)
    assert doc.title == "note"
    assert doc.filetype == ".md"
    assert "simple content" in doc.text
    assert isinstance(doc.updated_at, date)


def test_load_files(tmp_path):
    f1 = tmp_path / "a.md"
    f1.write_text("one")
    f2 = tmp_path / "b.md"
    f2.write_text("two")

    loader = DocumentLoader(config=Config())
    docs = loader.load_files([str(f1), str(f2)])
    assert len(docs) == 2
    titles = [d.title for d in docs]
    assert "a" in titles and "b" in titles