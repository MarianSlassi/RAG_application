import os
from datetime import datetime, date

from PyPDF2 import PdfReader
from docx import Document as DocxDocument

from src.schemas import Document
from src.helpers import Config

'''
1. If the DocumentLoader object initialized without passing path it will initialize config 
'''
class DocumentLoader():
    """
    Class for loading text from files/documents and transform them into list of dicts with files text and metadata.\n

    Used to transform files/documents into list[dict] with the format of a Document: \n
    {\n
    "title": "equipment",\n
    "path": "data/tinyco/equipment.md",\n
    "filetype": "md",\n
    "updated_at": "2025-08-25",\n
    "text": "…full plain text…"\n
    }\n
    """
    def __init__(self, config = Config ):
        """
        Pass config instance when initializing to have manageable source data location paths
        Args:
            config(Config):
                Custom object to store configs
        """
        self.config = config

    
    def find_files(self, path: str | None = None , allowed_ext: tuple = ('.md', '.pdf', '.docx')) -> list[str]:
        """
        Returns strings of paths to all files inside of directory and all sub directories
        Args:
            path:
                Load documents from *path* or fall back to canonical config directory.
            allowed_ext (tuple[str], optional):
                Tuple of strings with extensions to search, by default: ('.md', '.pdf', '.docx')
        Returns:
            list[str] : list of absolute paths to all files of a type
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
    
    def _extract_text(self, file):
        """
        Extracting text from file\n
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
        
    def _parse_file(self, file) -> Document:
        """
        Invokes self._extract_text() to get plain text from file, also extracts metadata (see "Returns")\n
        Assigns header of document by its first line. And updated_at when line starts with "updated"
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
        if os.path.isfile(file):
            file_content = self._extract_text(file)

        _, ext = os.path.splitext(file)
        title = None
        updated_at = None

        for line in file_content.splitlines():
            if title is None and line.strip():
                if line.startswith("#"):
                    title = line.replace("#", "").strip()
                else:
                    title = line.strip()

            if updated_at is None and line.lower().startswith("updated:"):
                date_str = line.split(":", 1)[1].strip()
                updated_at = datetime.strptime(date_str, "%Y-%m-%d")

            if title and updated_at:
                break
        if not title:
            title = os.path.basename(file)

        return Document(title=title, path=file, filetype=ext, updated_at=updated_at, text=file_content)
    
    def _load_files(self, files: list[str] = None) -> list[Document]:
        """
        Uses _parse_file() to construct list[Document]\n
        Args:
            files(list[str]):
                Assembling parsed files into list
        """
        if not files:
            files = self.find_files()
        files_list = []
        for file in files:
            file_metadata = self._parse_file(file=file)
            files_list.append(file_metadata)

        return files_list

