from sqlalchemy.ext.asyncio import AsyncSession

from .models import AuthType, AuthTypeEnum
from .repository import AuthTypeRepo


class AuthTypeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.auth_type_repo = AuthTypeRepo(session)

    async def get_auth_type_by_type(self, auth_type: AuthTypeEnum) -> AuthType:
        """
        Retrieve an auth type by its enum value.
        """
        result = await self.auth_type_repo.get_by_type(auth_type)
        if not result:
            raise ValueError(f"Auth type '{auth_type}' not found.")
        return result

    async def get_auth_type_by_name(self, name: str) -> AuthType:
        """
        Retrieve an auth type by its name.
        """
        result = await self.auth_type_repo.get_by_name(name)
        if not result:
            raise ValueError(f"Auth type '{name}' not found.")
        return result
