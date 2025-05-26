from pydantic import BaseModel

class GenerateDocument(BaseModel):
    """
    Schema for generating a document.
    """
    document_id: str
    