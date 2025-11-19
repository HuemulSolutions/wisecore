from pydantic import BaseModel
from typing import List, Optional

class CreateDocumentSection(BaseModel):
    """
    Schema for creating a template section.
    """
    name: str
    document_id: str
    prompt: str
    dependencies: Optional[List[str]] = None  # Optional field, can be None
    type: str = "text"  # Optional field, can be None
    
    
class UpdateSection(BaseModel):
    """
    Schema for updating a template section.
    """
    name: str
    prompt: str
    dependencies: Optional[List[str]] = None  # Optional field, can be None

    
class SectionOrder(BaseModel):
    """
    Schema for ordering template sections.
    """
    section_id: str
    order: int 
    
class UpdateSectionOrder(BaseModel):
    """
    Schema for updating the order of template sections.
    """
    new_order: List[SectionOrder]
    