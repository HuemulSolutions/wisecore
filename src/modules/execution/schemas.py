from pydantic import BaseModel

class UpdateLLM(BaseModel):
    """
    Schema for updating the LLM used in an execution.
    """
    llm_id: str