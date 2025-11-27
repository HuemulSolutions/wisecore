from functools import lru_cache

from .base import BaseEmbeddings
from .azure_openai import AzureOpenAIEmbeddings


@lru_cache(maxsize=1)
def get_embedding_model(provider) -> BaseEmbeddings:

    if provider == "azure_openai":
        return AzureOpenAIEmbeddings()

    raise ValueError(f"Embeddings provider '{provider}' no soportado")