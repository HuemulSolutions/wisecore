from pydantic import BaseModel
from typing import Optional

class GenerateDocument(BaseModel):
    """
    Schema for generating a document.
    """
    document_id: str
    execution_id: str
    instructions: Optional[str] = None
    
class FixSection(BaseModel):
    """
    Schema for fixing a section in a document.
    """
    content: str
    instructions: str
    
class RedactSectionPrompt(BaseModel):
    """
    Schema for redacting or improving the prompt for a section.
    """
    name: str
    content: Optional[str] = None  # Optional field, can be None