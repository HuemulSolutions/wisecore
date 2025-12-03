from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.models import User, UserStatus
from .repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def list_users(self) -> list[User]:
        """
        Return all users.
        """
        return await self.user_repo.get_all()

    async def approve_user(self, user_id: str) -> User:
        """
        Approve a pending user.
        """
        return await self._update_user_status(user_id, UserStatus.ACTIVE)

    async def reject_user(self, user_id: str) -> User:
        """
        Reject a pending user.
        """
        return await self._update_user_status(user_id, UserStatus.REJECTED)

    async def delete_user(self, user_id: str) -> None:
        """
        Delete a user by ID.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")

        await self.user_repo.delete(user)

    async def update_user_info(
        self,
        user_id: str,
        name: Optional[str] = None,
        last_name: Optional[str] = None,
        birthdate: Optional[datetime] = None,
    ) -> User:
        """
        Update basic user information.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")

        if name is None and last_name is None and birthdate is None:
            raise ValueError("No se proporcionaron datos para actualizar.")

        if name is not None:
            sanitized_name = name.strip()
            if not sanitized_name:
                raise ValueError("El nombre no puede estar vacío.")
            user.name = sanitized_name

        if last_name is not None:
            sanitized_last_name = last_name.strip()
            if not sanitized_last_name:
                raise ValueError("El apellido no puede estar vacío.")
            user.last_name = sanitized_last_name

        if birthdate is not None:
            # Store timezone-naive datetime to match existing model usage.
            user.birthdate = (
                birthdate.replace(tzinfo=None)
                if birthdate.tzinfo and birthdate.tzinfo.utcoffset(birthdate) is not None
                else birthdate
            )

        await self.user_repo.update(user)
        return user

    async def _update_user_status(self, user_id: str, status: UserStatus) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")

        if user.status != UserStatus.PENDING:
            raise ValueError(
                "Solo se pueden aprobar o rechazar usuarios en estado pendiente."
            )

        user.status = status.value
        if status == UserStatus.ACTIVE:
            user.activated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.user_repo.update(user)
        return user
