import os
from datetime import datetime, date

from PyPDF2 import PdfReader
from docx import Document as DocxDocument

from ..helpers import Config

from src.qabot.repository.models import DocumentRecord
from src.qabot.repository.models import ChunkRecord

import hashlib

from pathlib import Path

class DocumentLoader():
    """
    Class used to transform paths to documents list into list[Document] object\n
    Document format is a: \n
    {\n
    "title": "092_setting-up-a-secure-connection-to-a-company-issued-website",\n
    "path": "data/tinyco/equipment.md",\n
    "filetype": "md",\n
    "updated_at": "2025-08-25",\n
    "text": "…full plain text…"\n
    }\n
    """
    def __init__(self, config: Config | None ):
        """
        Pass config instance when initializing to have manageable source data location paths
        Args:
            config(Config):
                Custom object to store configs, used to fallback to 'canonical_dir' when searching for files
        """
        self.config = config or Config()

    
    def find_files(self, path: str | Path | None=None , allowed_ext: tuple=('.md', '.pdf', '.docx')) -> list[str]:
        """
        Returns strings of paths to all files inside of directory and all sub directories
        Args:
            path:
                Load documents from *path* or fall back to canonical config directory.
            allowed_ext (tuple[str], optional):
                Tuple of strings with extensions to search, by default: ('.md', '.pdf', '.docx')
        Returns:
            list[str] : list of absolute paths to all files of a type
        Note:
            You can use allowed_ext argument to find path to any types of files, but files parsing methods of this class bounded to default values, keep in mind it in case of need further processing of found files with nondefault extensions
        """
        

        if path is None:
            path = self.config.get('canonical_dir')
        elif not os.path.isdir(path):
            raise ValueError(
                "Parameter `path` must point to an existing directory."
            )

        if not path:
            raise ValueError("Path isn't in the object")

        files = []
        if allowed_ext is None:
            allowed_ext = ('.md', '.pdf', '.docx')
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(allowed_ext):
                    files.append(os.path.join(root, filename))

        return files
    
    def _extract_text(self, file:str):
        """
        Extracting text from file with given path to file\n
        Allowed extensions: from .md, .pdf, .docx files\n
        Yet only fixed type of formats\n
        Uses PyPDF2 and python-docx.
        Args:
            file(str):
                path to the file
        Returns:
            str
        """
        if file.endswith('.pdf'):
            text = ""
            with open(file, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text
        elif file.endswith('.docx'):
            doc = DocxDocument(file)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text
        else:
            with open(file, "r", encoding="utf-8") as f:
                return f.read()
        
    def _parse_file(self, file:str) -> DocumentRecord:
        """
        Takes file path and produce Document with metadata\n
        Invokes self._extract_text() to get plain text from file, also extracts metadata (see "Returns")\n
        Assigns 'title' of document by name of the file. And updated_at when line starts with "updated" or fallback to the system metainformation
        Args:
            file(str):
                path to file from which we will extract text and metadata
        Returns:
            Document:
                {\n
                "title": "equipment",\n
                "path": "data/tinyco/equipment.md",\n
                "filetype": "md",\n
                "updated_at": "2025-08-25",\n
                "text": "…full plain text…"\n
                }\n
        """
        if os.path.isfile(file): # Extracting text
            file_content = self._extract_text(file)
        content_hash = self._content_hash(file_content) # Getting text hash
        size_bytes = os.path.getsize(file) # Getting bytes size of a file
        _, ext = os.path.splitext(file) # getting full path to file with extension
        title = None
        updated_at = None

        for line in file_content.splitlines():

            if updated_at is None and line.lower().startswith("updated:"):
                date_str = line.split(":", 1)[1].strip()
                updated_at = datetime.strptime(date_str, "%Y-%m-%d")
                break

        if title is None:
            title = os.path.splitext(os.path.basename(file))[0]

        if updated_at is None:
            updated_at = datetime.fromtimestamp(os.path.getmtime(file))

        return DocumentRecord(doc_id = None, source_type=ext, source_uri=file, size_bytes=size_bytes, content_hash=content_hash, title=title,  updated_at=updated_at, content=file_content)
    
    def _content_hash(self, text:str) -> str:
        """
        Uses SHA256 to encode input string. 
        Returns:
            str: in hexadecimal format
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def load_files(self, files: list[str] | None = None) -> list[DocumentRecord]:
        """
        Uses _parse_file(file_path) method to assembley object of list[Document]\n
        Args:
            files(list[str]):
                paths to files,if not provided by default calls self.find_files() with canonical dir
        Returns:
            list[Document]
        """
        if not files:
            files = self.find_files()
        files_list = []
        for file in files:
            file_metadata = self._parse_file(file=file)
            files_list.append(file_metadata)

        return files_list

