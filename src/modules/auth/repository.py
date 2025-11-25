from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.base_repo import BaseRepository
from .models import CodePurpose, LoginCode, User


class UserRepo(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Return a user by email."""
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Return a user by username."""
        query = select(self.model).where(self.model.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class LoginCodeRepo(BaseRepository[LoginCode]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LoginCode)

    async def get_latest(
        self, email: str, purpose: CodePurpose, user_id: Optional[str] = None
    ) -> Optional[LoginCode]:
        """
        Return the most recent code for the given email/purpose (and user if provided).
        """
        query = select(self.model).where(
            self.model.email == email, self.model.purpose == purpose.value
        )
        if user_id:
            query = query.where(self.model.user_id == user_id)
        query = query.order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().first()
