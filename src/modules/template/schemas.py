from pydantic import BaseModel
from typing import Optional

class CreateTemplate(BaseModel):
    """
    Schema for creating a template.
    """
    name: str
    description: Optional[str] = None  # Optional field, can be None
    
    

class UpdateTemplate(BaseModel):
    """
    Schema for updating a template's name and/or description.
    """
    name: Optional[str] = None
    description: Optional[str] = None