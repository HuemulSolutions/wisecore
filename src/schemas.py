from pydantic import BaseModel, Field
from datetime import datetime
from datetime import timezone
from typing import Union

class ResponseSchema(BaseModel):
    data: Union[dict, list]
    transaction_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    

class GenerateDocument(BaseModel):
    """
    Schema for generating a document.
    """
    document_id: str
    
    
class CreateTemplate(BaseModel):
    """
    Schema for creating a template.
    """
    name: str
    
class CreateTemplateSection(BaseModel):
    """
    Schema for creating a template section.
    """
    name: str
    template_id: str
    order: int
    prompt: str
    type: str = "text"  # Optional field, can be None
    
    
class CreateTemplateSectionDependency(BaseModel):
    """
    Schema for creating a dependency between template sections.
    """
    section_id: str
    depends_on_id: str
    
