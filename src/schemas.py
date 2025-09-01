from pydantic import BaseModel, Field
from datetime import datetime
from datetime import timezone
from typing import Union, Optional, List

class ResponseSchema(BaseModel):
    data: Union[dict, list]
    transaction_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    

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
    
    
class CreateTemplate(BaseModel):
    """
    Schema for creating a template.
    """
    name: str
    organization_id: str
    description: Optional[str] = None  # Optional field, can be None
    
class CreateTemplateSection(BaseModel):
    """
    Schema for creating a template section.
    """
    name: str
    template_id: str
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
    
class CreateDocument(BaseModel):
    """
    Schema for creating a document.
    """
    name: str
    description: str
    organization_id: str
    document_type_id: str
    template_id: Optional[str] = None  # Optional field, can be None

class CreateDocumentDependency(BaseModel):
    """
    Schema for creating a dependency between document sections.
    """
    depends_on_document_id: str
    section_id: Optional[str] = None
    depends_on_section_id: Optional[str] = None
    
class CreateDocumentSection(BaseModel):
    """
    Schema for creating a template section.
    """
    name: str
    document_id: str
    prompt: str
    dependencies: Optional[List[str]] = None  # Optional field, can be None
    type: str = "text"  # Optional field, can be None
    
    
    
class AddDocumentContextText(BaseModel):
    """
    Schema for adding context text to a document.
    """
    name: str
    content: str
    
    
class ModifySection(BaseModel):
    """
    Schema for modifying a section's content.
    """
    content: str
    
class UpdateLLM(BaseModel):
    """
    Schema for updating the LLM used in an execution.
    """
    llm_id: str
    
    
class CreateOrganization(BaseModel):
    """
    Schema for creating an organization.
    """
    name: str
    description: Optional[str] = None  # Optional field, can be None


class CreateDocumentType(BaseModel):
    """
    Schema for creating a document type.
    """
    name: str
    color: str