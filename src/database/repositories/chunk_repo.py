from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from openai import AzureOpenAI
from ..models import Chunk, SectionExecution, Execution, Document
from src.config import system_config
from typing import List


DISTANCE = 0.75  # Similarity threshold

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
        
    async def create_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Create multiple chunks in the database.
        """
        self.session.add_all(chunks)
        await self.session.commit()
        for chunk in chunks:
            await self.session.refresh(chunk)
        return chunks
        
    async def search_by_embedding(self, embedded_query: str, limit: int = 5) -> List[dict]:
        """
        Search for chunks by embedding similarity.
        """
        distance = self.model.embedding.cosine_distance(embedded_query).label("distance")
        query = (
            select(self.model)
            .options(
                joinedload(self.model.section_execution).joinedload(SectionExecution.execution).joinedload(Execution.document)
            )
            .where(distance <= DISTANCE)
            .order_by(distance)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        chunks = result.scalars().unique().all()
        
        # Return chunks with additional information
        enriched_chunks = []
        for chunk in chunks:
            chunk_data = {
                'content': chunk.content,
                'execution_id': chunk.section_execution.execution_id,
                'document_id': chunk.section_execution.execution.document_id,
                'document_name': chunk.section_execution.execution.document.name,
                'section_execution_name': chunk.section_execution.name
            }
            enriched_chunks.append(chunk_data)
        
        return enriched_chunks
    
    async def delete_chunks_by_execution_id(self, execution_id: str) -> int:
        """
        Delete chunks associated with a specific execution ID.
        Returns the number of deleted chunks.
        """
        query = (
            select(Chunk)
            .join(Chunk.section_execution)
            .where(SectionExecution.execution_id == execution_id)
        )
        result = await self.session.execute(query)
        chunks_to_delete = result.scalars().all()
        
        if not chunks_to_delete:
            return 0
        
        for chunk in chunks_to_delete:
            await self.session.delete(chunk)
        
        await self.session.commit()
        return len(chunks_to_delete)
    
    
    
                