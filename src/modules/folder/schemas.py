from pydantic import BaseModel, model_validator
from typing import Optional

class CreateNewFolder(BaseModel):
    """
    Schema for creating a new folder.
    """
    name: str
    organization_id: Optional[str] = None
    parent_folder_id: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_folder_parent(self):
        if self.organization_id is None and self.parent_folder_id is None:
            raise ValueError('Al menos uno de organization_id o parent_folder_id debe ser proporcionado')
        return self