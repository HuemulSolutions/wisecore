from pydantic import BaseModel
from typing import List, Optional

class CreateTemplateSection(BaseModel):
    """
    Schema for creating a template section.
    """
    name: str
    template_id: str
    prompt: str
    dependencies: Optional[List[str]] = None  # Optional field, can be None
    type: str = "text"  # Optional field, can be None
    
class UpdateTemplateSection(BaseModel):
    """
    Schema for updating a template section.
    """
    name: str
    prompt: str
    dependencies: Optional[List[str]] = None  # Optional field, can be None
    
class CreateTemplateSectionDependency(BaseModel):
    """
    Schema for creating a dependency between template sections.
    """
    section_id: str
    depends_on_id: str
    
    
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
    