from functools import lru_cache
from typing import Optional
from .base import SecretProvider
from .azure import AzureKeyVaultProvider
from .hashicorp import HashiCorpVaultProvider
from .local import LocalFileSecretProvider
from src.config import system_config

@lru_cache(maxsize=1)
def get_provider() -> SecretProvider:
    backend = system_config.SECRETS_PROVIDER

    if backend == "azure":
        return AzureKeyVaultProvider()
    if backend == "hashicorp":
        return HashiCorpVaultProvider()
    if backend == "local":
        return LocalFileSecretProvider()

    raise ValueError(f"SECRETS_PROVIDER '{backend}' no soportado")

def get_secret(name: str) -> Optional[str]:
    return get_provider().get_secret(name)

def set_secret(value: str) -> str:
    return get_provider().set_secret(value)
