from pydantic import BaseModel
from datetime import date

class Document(BaseModel):
    title: str
    path: str
    filetype: str
    updated_at: date
    text: str