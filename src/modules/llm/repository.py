from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, update
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

    async def find_by_name(self, name: str) -> LLM | None:
        """
        Return an LLM by name without raising if it does not exist.
        """
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def find_by_internal_name(self, internal_name: str) -> LLM | None:
        """
        Return an LLM by internal identifier without raising if it does not exist.
        """
        query = select(self.model).where(self.model.internal_name == internal_name)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

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

    async def _get_default_llm(self) -> LLM | None:
        """
        Internal method to retrieve the default LLM.
        Returns the LLM marked as default, or the first available LLM if none is marked as default.
        """
        # First, try to get LLM marked as default
        default_query = select(self.model).where(self.model.is_default == True)
        default_result = await self.session.execute(default_query)
        default_llm = default_result.scalars().one_or_none()

        if default_llm:
            return default_llm

        # If no default LLM, return the first available LLM
        first_query = select(self.model).limit(1)
        first_result = await self.session.execute(first_query)
        return first_result.scalars().one_or_none()

    async def set_as_default(self, llm_id: str) -> LLM:
        """
        Set an LLM as default and unset all others.
        """
        # First, unset all LLMs as default
        await self.session.execute(
            update(self.model).values(is_default=False)
        )

        # Then set the specified LLM as default
        await self.session.execute(
            update(self.model)
            .where(self.model.id == llm_id)
            .values(is_default=True)
        )

        # Return the updated LLM
        return await self.get_by_id(llm_id)
