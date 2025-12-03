from sqlalchemy.ext.asyncio import AsyncSession

from .models import AuthType, AuthTypeEnum
from .repository import AuthTypeRepo


SUPPORTED_AUTH_TYPES = [auth_type.value for auth_type in AuthTypeEnum]


class AuthTypeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.auth_type_repo = AuthTypeRepo(session)

    def get_supported_types(self) -> list[str]:
        """
        Expose the auth types supported by the platform.
        """
        return SUPPORTED_AUTH_TYPES.copy()

    async def get_all_auth_types(self) -> list[AuthType]:
        """
        Retrieve all configured auth types.
        """
        return await self.auth_type_repo.get_all()

    async def get_auth_type_by_id(self, auth_type_id: str) -> AuthType:
        """
        Retrieve an auth type by its identifier.
        """
        auth_type = await self.auth_type_repo.get_by_id(auth_type_id)
        if not auth_type:
            raise ValueError(f"Auth type with id {auth_type_id} not found.")
        return auth_type

    async def get_auth_type_by_type(self, auth_type: AuthTypeEnum) -> AuthType | None:
        """
        Retrieve an auth type by its enum type.
        """
        return await self.auth_type_repo.get_by_type(auth_type)

    async def create_auth_type(
        self,
        name: str,
        auth_type: AuthTypeEnum,
        params: dict | None = None,
    ) -> AuthType:
        """
        Create a new auth type with optional parameters.
        """
        sanitized_name = name.strip() if name else ""
        if not sanitized_name:
            raise ValueError("Auth type name cannot be empty.")

        if auth_type.value not in SUPPORTED_AUTH_TYPES:
            raise ValueError(f"Auth type '{auth_type}' is not supported.")

        existing_by_name = await self.auth_type_repo.get_by_name(sanitized_name)
        if existing_by_name:
            raise ValueError(f"Auth type with name '{sanitized_name}' already exists.")

        auth_type_model = AuthType(
            name=sanitized_name,
            type=auth_type,
            params=params or {},
        )
        return await self.auth_type_repo.add(auth_type_model)

    async def update_auth_type(
        self,
        auth_type_id: str,
        name: str | None = None,
        auth_type: AuthTypeEnum | None = None,
        params: dict | None = None,
    ) -> AuthType:
        """
        Update an auth type's metadata or parameters.
        """
        auth_type_model = await self.get_auth_type_by_id(auth_type_id)

        if name is not None:
            sanitized_name = name.strip()
            if not sanitized_name:
                raise ValueError("Auth type name cannot be empty.")
            existing_by_name = await self.auth_type_repo.get_by_name(sanitized_name)
            if existing_by_name and existing_by_name.id != auth_type_model.id:
                raise ValueError(f"Auth type with name '{sanitized_name}' already exists.")
            auth_type_model.name = sanitized_name

        if auth_type is not None:
            if auth_type.value not in SUPPORTED_AUTH_TYPES:
                raise ValueError(f"Auth type '{auth_type}' is not supported.")
            auth_type_model.type = auth_type

        if params is not None:
            auth_type_model.params = params

        return await self.auth_type_repo.update(auth_type_model)
