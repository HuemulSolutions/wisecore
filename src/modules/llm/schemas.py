from pydantic import BaseModel


class CreateLLM(BaseModel):
    """
    Schema for registering a new LLM model.
    """
    name: str
    internal_name: str
    provider_id: str


class SetDefaultLLM(BaseModel):
    """
    Schema for setting a default LLM model.
    """
    llm_id: str
