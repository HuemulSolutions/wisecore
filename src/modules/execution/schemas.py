from pydantic import BaseModel, model_validator
from typing import Optional

class UpdateLLM(BaseModel):
    """
    Schema for updating the LLM used in an execution.
    """
    llm_id: str
    
class GenerateDocument(BaseModel):
    """
    Schema for generating a document.
    """
    document_id: str
    llm_id: str
    execution_id: Optional[str] = None
    instructions: Optional[str] = None
    start_section_id: Optional[str] = None
    single_section_mode: Optional[bool] = False
    
    @model_validator(mode='after')
    def validate_start_section_requires_execution(self):
        if self.start_section_id is not None and self.execution_id is None:
            raise ValueError("start_section_id requiere que se proporcione execution_id")
        return self