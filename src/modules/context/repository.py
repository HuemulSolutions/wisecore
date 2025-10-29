from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Context

class ContextRepo(BaseRepository[Context]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Context)
        
    async def get_by_document_id(self, document_id: str):
        """
        Retrieve contexts by document ID.
        """
        query = select(self.model).where(self.model.document_id == document_id)
        result = await self.session.execute(query)
        return result.scalars().all()