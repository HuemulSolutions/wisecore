from typing import Optional

from pydantic import BaseModel


class ProviderBase(BaseModel):
    name: str
    key: Optional[str] = None
    endpoint: Optional[str] = None
    deployment: Optional[str] = None


class CreateProvider(ProviderBase):
    """
    Schema for creating a new LLM provider.
    """
    ...


class UpdateProvider(BaseModel):
    """
    Schema for updating an existing LLM provider.
    """
    name: Optional[str] = None
    key: Optional[str] = None
    endpoint: Optional[str] = None
    deployment: Optional[str] = None
