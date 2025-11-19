from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Organization

class OrganizationRepo(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Organization)
        
    async def get_by_name(self, name: str) -> Organization:
        """
        Retrieve an organization by its name.
        """
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        organization = result.scalars().one_or_none()
        return organization