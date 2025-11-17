from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from .repository import LLMRepo
from .models import LLM
from src.modules.llm_provider.service import LLMProviderService
from .utils import get_llm
from langchain_core.language_models import BaseChatModel

class LLMService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm_repo = LLMRepo(session)
        self.provider_service = LLMProviderService(session)

    async def get_all_llms(self) -> list[LLM]:
        """
        Retrieve all LLMs.
        """
        llms = await self.llm_repo.get_all()
        return llms

    async def get_llm_by_name(self, name: str) -> LLM:
        """
        Retrieve an LLM by its name.
        """
        llm = await self.llm_repo.get_by_name(name)
        if not llm:
            raise ValueError(f"LLM with name {name} not found.")
        return llm

    async def create_llm(self, name: str, internal_name: str, provider_id: str) -> LLM:
        """
        Create a new LLM ensuring the referenced provider exists.
        """
        if not name or not name.strip():
            raise ValueError("LLM name cannot be empty.")

        if not internal_name or not internal_name.strip():
            raise ValueError("LLM internal_name cannot be empty.")

        if not provider_id:
            raise ValueError("provider_id is required to create an LLM.")

        provider = await self.provider_service.get_provider_by_id(provider_id)

        normalized_name = name.strip()
        normalized_internal_name = internal_name.strip()

        if await self.llm_repo.find_by_name(normalized_name):
            raise ValueError(f"LLM with name {normalized_name} already exists.")

        if await self.llm_repo.find_by_internal_name(normalized_internal_name):
            raise ValueError(f"LLM with internal_name {normalized_internal_name} already exists.")

        llm = LLM(
            name=normalized_name,
            internal_name=normalized_internal_name,
            provider_id=str(provider.id),
        )
        return await self.llm_repo.add(llm)

    async def check_llm_exists(self, llm_id: str) -> bool:
        """
        Check if an LLM exists by its ID.
        """
        llm = await self.llm_repo.get_by_id(llm_id)
        return llm

    async def update_llm(
        self,
        llm_id: str,
        name: Optional[str] = None,
        internal_name: Optional[str] = None,
        provider_id: Optional[str] = None,
    ) -> LLM:
        """
        Update mutable attributes of an existing LLM.
        """
        if not llm_id:
            raise ValueError("LLM ID is required.")

        llm = await self.llm_repo.get_by_id(llm_id)
        if not llm:
            raise ValueError(f"LLM with id {llm_id} not found.")

        if all(value is None for value in (name, internal_name, provider_id)):
            raise ValueError("No data provided to update the LLM.")

        if name is not None:
            sanitized_name = name.strip()
            if not sanitized_name:
                raise ValueError("LLM name cannot be empty.")

            existing_by_name = await self.llm_repo.find_by_name(sanitized_name)
            if existing_by_name and existing_by_name.id != llm.id:
                raise ValueError(f"LLM with name {sanitized_name} already exists.")

            llm.name = sanitized_name

        if internal_name is not None:
            sanitized_internal = internal_name.strip()
            if not sanitized_internal:
                raise ValueError("LLM internal_name cannot be empty.")

            existing_by_internal = await self.llm_repo.find_by_internal_name(sanitized_internal)
            if existing_by_internal and existing_by_internal.id != llm.id:
                raise ValueError(f"LLM with internal_name {sanitized_internal} already exists.")

            llm.internal_name = sanitized_internal

        if provider_id is not None:
            if not provider_id.strip():
                raise ValueError("provider_id cannot be empty.")

            provider = await self.provider_service.get_provider_by_id(provider_id)
            llm.provider_id = str(provider.id)

        return await self.llm_repo.update(llm)

    async def get_llm_by_execution_id(self, execution_id: str) -> BaseChatModel:
        """
        Retrieve an LLM associated with a specific execution ID.
        """
        llm = await self.llm_repo.get_by_execution_id(execution_id)
        model = await self.get_model(llm.id)
        return model
    
    async def get_model(self, llm_id: str = None) -> BaseChatModel:
        """
        Retrieve an LLM instance by its ID.
        """
        if llm_id is None:
            llm = await self.get_default_llm()
        else:
            llm = await self.llm_repo.get_by_id(llm_id)
            if not llm:
                raise ValueError(f"LLM with id {llm_id} not found.")
        
        provider = await self.provider_service.get_provider_with_secrets(llm.provider_id)
        model_info = {
            "name": llm.internal_name,
            "provider": provider['name'],
            "key": provider['key'],
            "endpoint": provider['endpoint'],
            "deployment": provider['deployment']
        }
        model = get_llm(model_info)
        return model

    async def get_default_llm(self) -> LLM:
        """
        Retrieve the default LLM.
        Returns the LLM marked as default, or the single LLM if only one exists.
        """
        llm = await self.llm_repo._get_default_llm()
        if not llm:
            raise ValueError("No default LLM found. You must create an LLM first.")
        return llm
    
    async def set_default_llm(self, llm_id: str) -> LLM:
        """
        Set an LLM as the default one.
        Only one LLM can be default at a time.
        """
        if not llm_id:
            raise ValueError("LLM ID is required.")
        
        # Check if LLM exists
        llm = await self.llm_repo.get_by_id(llm_id)
        if not llm:
            raise ValueError(f"LLM with id {llm_id} not found.")
        
        # Set as default
        return await self.llm_repo.set_as_default(llm_id)
