from pydantic import BaseModel

class ModifySectionExecutionSchema(BaseModel):
    new_content: str