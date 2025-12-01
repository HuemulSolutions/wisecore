from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from .models import Chunk
from src.modules.section_execution.models import SectionExecution
from src.modules.execution.models import Execution
from src.modules.document.models import Document
from typing import List


DISTANCE = 0.75  # Similarity threshold

class ChunkRepo(BaseRepository[Chunk]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Chunk)
    
    
    async def get_execution_to_chunking(self, execution_id: str) -> Execution:
        """
        Retrieve an execution by its ID with the associated section executions
        """
            
        query = (select(Execution)
                 .options(joinedload(Execution.sections_executions))
                 .where(Execution.id == execution_id))
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
        
    async def create_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Create multiple chunks in the database.
        """
        self.session.add_all(chunks)
        await self.session.commit()
        for chunk in chunks:
            await self.session.refresh(chunk)
        return chunks
        
    async def search_by_embedding(self, embedded_query: List[float], organization_id: str, limit: int = 25) -> List[Chunk]:
        """
        Search for chunks by embedding similarity.
        """
        distance = self.model.embedding.cosine_distance(embedded_query).label("distance")
        query = (
            select(self.model)
            .join(Chunk.section_execution)
            .join(SectionExecution.execution)
            .join(Execution.document)
            .options(
                joinedload(self.model.section_execution)
                .joinedload(SectionExecution.execution)
                .joinedload(Execution.document)
            )
            .where(distance <= DISTANCE)
            .where(Document.organization_id == organization_id)
            .order_by(distance)
            # .limit(limit)
        )
        
        result = await self.session.execute(query)
        chunks = result.scalars().unique().all()
        

        
        return chunks
    
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
            raise ValueError(f"No chunks found for execution ID {execution_id}.")
        
        for chunk in chunks_to_delete:
            await self.session.delete(chunk)
        
        await self.session.commit()
        return len(chunks_to_delete)
