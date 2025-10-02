from pydantic import BaseModel, Field
from datetime import date

class Meta(BaseModel):
    section_id: int = Field(..., ge=0, description="Section number, non-negative")
    section_title: str = Field("", max_length=200, description="Section title (can be empty)")
    document_title: str = Field(..., min_length=1, max_length=300, description="Document title")
    path: str = Field(..., pattern=r"data/.+\.(pdf|md|docx)$", description="Path to file inside the data/ directory")
    tokens: int = Field(..., ge=1, le=2048, description="Number of tokens in the chunk")
    updated_at: date = Field(...,description="Last time when parent document of chunk was added")

class Chunk(BaseModel):
    id: str = Field(..., pattern=r"^[\w\-]+_\d+$", description="ID in format slug_section_subsection")
    text: str = Field(..., min_length=1, description="Chunk text")
    meta: Meta


# Old 'id' field pattern    id: str = Field(..., pattern=r"^[\w\-]+_\d+_\d+$", description="ID in format slug_section_subsection")


# Naive Mocking template:
# Chunk(
#     id="094_configuring-a-company-issued-device-for-international-travel_0_1",
#     text="Select the international...",
#     meta= Meta(
#             document_title= "094_configuring-a-company-issued-device-for-international-travel",
#             path= "data/it-knowledge/canonical/pdf/094_configuring-a-company-issued-device-for-international-travel.pdf",
#             section_id= 0,
#             section_title= "None",
#             #sub_section_id= 1,
#             tokens= 256
#     )
# )