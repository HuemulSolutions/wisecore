from pydantic import BaseModel
from typing import Optional

class CreateOrganization(BaseModel):
    """
    Schema for creating an organization.
    """
    name: str
    description: Optional[str] = None  # Optional field, can be None