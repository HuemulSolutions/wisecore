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