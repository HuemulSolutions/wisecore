from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.secrets import get_provider as get_secret_provider
from .models import Provider
from .repository import LLMProviderRepo


SUPPORTED_PROVIDERS = {
    "azure_openai": 
        {"display": "Azure OpenAI", 
         "api_key": True,
         "endpoint": True,
         "deployment": True},
    "openai": 
        {"display": "OpenAI",
         "api_key": True,
         "endpoint": False,
         "deployment": False},
    "anthropic": 
        {"display": "Anthropic",
         "api_key": True,
         "endpoint": False,
         "deployment": False},
    "ibm_model_gateway": 
        {"display": "IBM Model Gateway",
         "api_key": True,
         "endpoint": True,
         "deployment": False},
}


class LLMProviderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.provider_repo = LLMProviderRepo(session)
        self.secret_provider = get_secret_provider()

    def get_supported_providers(self) -> list[str]:
        """
        Expose the providers currently supported by the platform.
        """
        return SUPPORTED_PROVIDERS.copy()

    async def get_all_providers(self) -> list[dict]:
        """
        Retrieve all registered providers with display names.
        """
        models = await self.provider_repo.get_all()
        
        return [
            {
                "id": provider.id,
                "name": provider.name,
                "display_name": SUPPORTED_PROVIDERS.get(provider.name, {}).get("display", provider.name)
            }
            for provider in models
        ]

    async def get_provider_by_id(self, provider_id: str) -> Provider:
        """
        Retrieve a single provider by its identifier.
        """
        provider = await self.provider_repo.get_by_id(provider_id)
        if not provider:
            raise ValueError(f"Provider with id {provider_id} not found.")
        return provider

    async def get_provider_with_secrets(self, provider_id: str) -> dict:
        """
        Retrieve a provider along with the decrypted secret values.
        """
        provider = await self.get_provider_by_id(provider_id)
        return {
            "id": provider.id,
            "name": provider.name,
            "created_at": provider.created_at,
            "updated_at": provider.updated_at,
            "key": self._retrieve_secret_value(provider.key),
            "endpoint": self._retrieve_secret_value(provider.endpoint),
            "deployment": self._retrieve_secret_value(provider.deployment),
        }

    async def create_provider(
        self,
        name: str,
        key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None,
    ) -> Provider:
        """
        Create a new provider, persisting sensitive data in the secrets backend.
        """
        if not name or not name.strip():
            raise ValueError("Provider name cannot be empty.")

        # Validate provider is supported
        if name.strip() not in SUPPORTED_PROVIDERS:
            supported_names = list(SUPPORTED_PROVIDERS.keys())
            raise ValueError(f"Provider '{name}' is not supported. Supported providers: {supported_names}")

        # Validate required credentials
        self._validate_required_credentials(name.strip(), key, endpoint, deployment)

        existing = await self.provider_repo.get_by_name(name.strip())
        if existing:
            raise ValueError(f"Provider with name {name} already exists.")

        provider = Provider(
            name=name.strip(),
            key=self._store_secret_value(key),
            endpoint=self._store_secret_value(endpoint),
            deployment=self._store_secret_value(deployment),
        )

        return await self.provider_repo.add(provider)

    async def update_provider(
        self,
        provider_id: str,
        name: Optional[str] = None,
        key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None,
    ) -> Provider:
        """
        Update provider metadata and optionally rotate stored secrets.
        """
        provider = await self.get_provider_by_id(provider_id)

        if name is not None:
            if not name.strip():
                raise ValueError("Provider name cannot be empty.")

            existing = await self.provider_repo.get_by_name(name.strip())
            if existing and existing.id != provider.id:
                raise ValueError(f"Provider with name {name} already exists.")

            provider.name = name.strip()

        if key is not None:
            provider.key = self._store_secret_value(key)

        if endpoint is not None:
            provider.endpoint = self._store_secret_value(endpoint)

        if deployment is not None:
            provider.deployment = self._store_secret_value(deployment)

        return await self.provider_repo.update(provider)

    async def delete_provider(self, provider_id: str) -> None:
        """
        Delete a provider by its identifier.
        """
        provider = await self.get_provider_by_id(provider_id)
        await self.provider_repo.delete(provider)

    def _store_secret_value(self, value: Optional[str]) -> Optional[str]:
        """
        Persist a sensitive value in the configured secrets provider.
        """
        if value is None:
            return None

        sanitized = value.strip()
        if not sanitized:
            raise ValueError("Secret values cannot be empty.")

        try:
            return self.secret_provider.set_secret(sanitized)
        except Exception as exc:
            raise ValueError(f"Failed to persist secret value: {str(exc)}")

    def _retrieve_secret_value(self, name: Optional[str]) -> Optional[str]:
        """
        Fetch a secret value from the configured secrets backend.
        """
        if not name:
            return None
        try:
            return self.secret_provider.get_secret(name)
        except Exception as exc:
            raise ValueError(f"Failed to retrieve secret value: {str(exc)}")

    def _validate_required_credentials(
        self, 
        provider_name: str, 
        key: Optional[str], 
        endpoint: Optional[str], 
        deployment: Optional[str]
    ) -> None:
        """
        Validate that required credentials are provided for the specified provider.
        """
        provider_config = SUPPORTED_PROVIDERS[provider_name]
        
        if provider_config["api_key"] and (not key or not key.strip()):
            raise ValueError(f"API key is required for provider '{provider_name}'.")
        
        if provider_config["endpoint"] and (not endpoint or not endpoint.strip()):
            raise ValueError(f"Endpoint is required for provider '{provider_name}'.")
        
        if provider_config["deployment"] and (not deployment or not deployment.strip()):
            raise ValueError(f"Deployment is required for provider '{provider_name}'.")
