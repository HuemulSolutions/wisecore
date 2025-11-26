from pydantic import BaseModel
from typing import Optional


class AddSectionExecutionSchema(BaseModel):
    name: str
    output: str
    after_from: Optional[str] = None

class ModifySectionExecutionSchema(BaseModel):
    new_content: str
