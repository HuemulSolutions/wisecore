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


class UpdateLLM(BaseModel):
    """
    Schema for partially updating an existing LLM model.
    """
    name: str | None = None
    internal_name: str | None = None
    provider_id: str | None = None
