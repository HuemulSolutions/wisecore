from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Execution

class ExecutionRepo(BaseRepository[Execution]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Execution)
        
    async def get_executions_by_doc_id(self, document_id: str)-> list:
        """
        Retrieve all executions for a specific document.
        """
        query = (select(self.model)
                 .where(self.model.document_id == document_id)
                 .order_by(self.model.created_at.desc()))
        result = await self.session.execute(query)
        executions = result.scalars().all()
        return executions if executions else []
