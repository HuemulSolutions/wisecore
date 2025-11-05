from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import LLM
from src.modules.execution.models import Execution

class LLMRepo(BaseRepository[LLM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LLM)
        
    async def get_by_name(self, name: str) -> LLM:
        """
        Retrieve an LLM by its name.
        """
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        llm = result.scalars().one_or_none()
        if not llm:
            raise ValueError(f"LLM with name {name} not found.")
        return llm
    
    async def get_by_execution_id(self, execution_id: str) -> LLM:
        """
        Retrieve an LLM associated with a specific execution ID.
        """
        query = (
            select(LLM)
            .join(Execution, LLM.id == Execution.model_id)
            .where(Execution.id == execution_id)
        )
        result = await self.session.execute(query)
        llm = result.scalars().one_or_none()
        if not llm:
            raise ValueError(f"No LLM found for execution ID {execution_id}.")
        return llm