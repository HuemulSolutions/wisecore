from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.llm_repo import LLMRepo
from src.database.models import LLM

class LLMService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm_repo = LLMRepo(session)
        
    async def get_all_llms(self):
        """
        Retrieve all LLMs.
        """
        llms = await self.llm_repo.get_all()
        return llms