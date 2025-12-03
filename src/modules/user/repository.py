from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.base_repo import BaseRepository
from src.modules.auth.models import User, UserStatus


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email.
        """
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_status(self, status: UserStatus) -> list[User]:
        """
        Retrieve all users matching a given status.
        """
        query = select(self.model).where(self.model.status == status.value)
        result = await self.session.execute(query)
        return result.scalars().all()
