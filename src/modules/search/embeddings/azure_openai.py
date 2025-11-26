from .base import BaseEmbeddings
from openai import AzureOpenAI
from src.config import system_config

class AzureOpenAIEmbeddings(BaseEmbeddings):
    
    def __init__(self):
        self.model = AzureOpenAI(
            api_key=system_config.AZURE_OPENAI_API_KEY,
            azure_endpoint=system_config.AZURE_OPENAI_ENDPOINT,
            api_version="2025-03-01-preview",
        )
        
    def generate_embeddings(self, text: str) -> list[float]:
        """
        Genera embeddings para el texto proporcionado utilizando Azure OpenAI.
        
        Args:
            text: Texto para generar embeddings
            
        Returns:
            Lista de floats que representan el embedding del texto
        """
        embedding = self.model.embeddings.create(
            model="text-embedding-3-large",
            input=text,
        )
        return embedding.data[0].embedding