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
