from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .models import LLM

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