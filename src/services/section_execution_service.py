from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.sectionexec_repo import SectionExecRepo
from src.database.models import SectionExecution

class SectionExecutionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.section_exec_repo = SectionExecRepo(session)
    
    async def delete_section_execution(self, section_execution_id: str):
        """
        Delete a section execution by its ID.
        """
        section_execution = await self.section_exec_repo.get_by_id(section_execution_id)
        if not section_execution:
            raise ValueError(f"Section execution with ID {section_execution_id} not found")
        
        await self.section_exec_repo.delete(section_execution)
        return True