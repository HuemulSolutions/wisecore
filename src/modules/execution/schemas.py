from pydantic import BaseModel
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
    execution_id: str
    instructions: Optional[str] = None
    start_section_id: Optional[str] = None
    single_section_mode: Optional[bool] = False