from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.base_repo import BaseRepository
from .models import Provider


class LLMProviderRepo(BaseRepository[Provider]):
    """
    Repository layer handling persistence for Provider entities.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Provider)

    async def get_by_name(self, name: str) -> Provider | None:
        """
        Retrieve a provider by its display name.
        """
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
    
    async def get_all(self) -> list[Provider]:
        """
        Retrieve all providers.
        """
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()
