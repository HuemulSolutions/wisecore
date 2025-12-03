from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.base_repo import BaseRepository
from .models import AuthType, AuthTypeEnum


class AuthTypeRepo(BaseRepository[AuthType]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AuthType)

    async def get_by_name(self, name: str) -> AuthType | None:
        """
        Retrieve an auth type by its unique name.
        """
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_type(self, auth_type: AuthTypeEnum) -> AuthType | None:
        """
        Retrieve an auth type by its enum type.
        """
        query = select(self.model).where(self.model.type == auth_type)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
