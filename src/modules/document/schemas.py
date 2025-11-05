from typing import Optional
from pydantic import BaseModel

class CreateDocument(BaseModel):
    """
    Schema for creating a document.
    """
    name: str
    description: str
    document_type_id: str
    template_id: Optional[str] = None  # Optional field, can be None
    
class CreateDocumentLibrary(BaseModel):
    """
    Schema for creating a document in the library.
    """
    name: str
    description: str 
    document_type_id: str
    template_id: Optional[str] = None  # Optional field, can be None
    folder_id: Optional[str] = None  # Optional field, can be None

class CreateDocumentDependency(BaseModel):
    """
    Schema for creating a dependency between document sections.
    """
    depends_on_document_id: str
    section_id: Optional[str] = None
    depends_on_section_id: Optional[str] = None
    

    
class UpdateDocument(BaseModel):
    """
    Schema for updating a document's name and/or description.
    """
    name: Optional[str] = None
    description: Optional[str] = None