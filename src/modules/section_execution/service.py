from sqlalchemy.ext.asyncio import AsyncSession
from .repository import SectionExecRepo

class SectionExecutionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.section_exec_repo = SectionExecRepo(session)
        
    async def get_by_id(self, section_execution_id: str):
        """
        Retrieve a section execution by its ID.
        """
        section_execution = await self.section_exec_repo.get_by_id(section_execution_id)
        if not section_execution:
            raise ValueError(f"Section execution with ID {section_execution_id} not found")
        return section_execution
    
    
    async def update_section_execution_content(self, section_execution_id: str, new_content: str):
        """
        Update the content of a section execution.
        """
        section_exec = await self.section_exec_repo.get_by_id(section_execution_id)
        if not section_exec:
            raise ValueError(f"Section execution with ID {section_execution_id} not found.")
        
        section_exec.custom_output = new_content
        updated_section_exec = await self.section_exec_repo.update(section_exec)
        return updated_section_exec
    
    async def delete_section_execution(self, section_execution_id: str):
        """
        Delete a section execution by its ID.
        """
        section_execution = await self.section_exec_repo.get_by_id(section_execution_id)
        if not section_execution:
            raise ValueError(f"Section execution with ID {section_execution_id} not found")
        
        await self.section_exec_repo.delete(section_execution)
        return True