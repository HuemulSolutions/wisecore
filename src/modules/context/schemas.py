from pydantic import BaseModel

class AddDocumentContextText(BaseModel):
    """
    Schema for adding context text to a document.
    """
    name: str
    content: str