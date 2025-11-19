from sqlalchemy.ext.asyncio import AsyncSession
from .repository import SectionExecRepo
from .models import SectionExecution

class SectionExecutionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.section_exec_repo = SectionExecRepo(session)
        
        
    async def add_section_execution(self, section_execution: SectionExecution) -> SectionExecution:
        """
        Add a new SectionExecution to the database.
        """
        created_section_execution = await self.section_exec_repo.add(section_execution)
        return created_section_execution 
        
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
    
    async def get_partial_section_execution_by_id(self, execution_id: str) -> SectionExecution:
        """
        Retrieve a partial section execution by its ID.
        """
        section_execution = await self.section_exec_repo.get_partial_sections_by_execution_id(execution_id)
        if not section_execution:
            return {}
        sections_dict = {}
        for sec_exec in section_execution:
            sections_dict[sec_exec.section_id] = sec_exec.custom_output if sec_exec.custom_output else sec_exec.output
        return sections_dict