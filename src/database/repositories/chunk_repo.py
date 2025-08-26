from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from openai import AzureOpenAI
from ..models import Chunk
from src.config import system_config

class ChunkRepo(BaseRepository[Chunk]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Chunk)
        
    @staticmethod
    async def _embed_text(text: str):
        """
        Generate an embedding for the given text.
        """
        azure_client = AzureOpenAI(
            api_key=system_config.AZURE_OPENAI_API_KEY,
            azure_endpoint=system_config.AZURE_OPENAI_ENDPOINT,
            api_version="2025-03-01-preview",
        )
        embedding = azure_client.embeddings.create(
            model="text-embedding-3-large",
            input=text,
        )
        return embedding.data[0].embedding
        
    async def search_by_embedding(self, text: str, organization_id: str = None, limit: int = 10):
        """
        Search for chunks by embedding similarity.
        """
        query = select(self.model).where(
            self.model.organization_id == organization_id,
            self.model.embedding.similarity(text) > 0.8
        ).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    
    
                