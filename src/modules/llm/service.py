from sqlalchemy.ext.asyncio import AsyncSession
from .repository import LLMRepo
from .models import LLM

class LLMService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm_repo = LLMRepo(session)
        
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
    
    async def check_llm_exists(self, llm_id: str) -> bool:
        """
        Check if an LLM exists by its ID.
        """
        llm = await self.llm_repo.get_by_id(llm_id)
        return llm