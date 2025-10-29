from pydantic import BaseModel

class CreateDocumentType(BaseModel):
    """
    Schema for creating a document type.
    """
    name: str
    color: str