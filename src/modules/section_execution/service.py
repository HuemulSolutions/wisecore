from sqlalchemy.ext.asyncio import AsyncSession
from .repository import SectionExecRepo
from .models import SectionExecution
from src.modules.execution.repository import ExecutionRepo

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

    async def add_section_execution_to_execution(self, execution_id: str, name: str, output: str,
                                                 after_from: str | None = None) -> SectionExecution:
        """
        Add a new SectionExecution for an execution, placing it after the specified section execution.
        """
        execution_repo = ExecutionRepo(self.session)
        execution = await execution_repo.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution with ID {execution_id} not found.")

        existing_sections = await self.section_exec_repo.get_execution_sections_ordered(execution_id)

        insertion_index = 0
        if after_from:
            insertion_index = None
            for idx, section_exec in enumerate(existing_sections):
                if str(section_exec.id) == str(after_from):
                    insertion_index = idx + 1
                    break
            if insertion_index is None:
                raise ValueError(f"Section execution with ID {after_from} not found in execution {execution_id}.")

        new_section_execution = SectionExecution(
            name=name,
            output=output,
            section_id=None,
            execution_id=execution_id,
            order=0
        )

        reordered_sections = (
            existing_sections[:insertion_index] + [new_section_execution] + existing_sections[insertion_index:]
        )
        for idx, section_exec in enumerate(reordered_sections, start=1):
            section_exec.order = idx

        await self.section_exec_repo.add(new_section_execution)
        await self.session.flush()
        return new_section_execution
    
    async def save_or_update_section_execution(self, section_execution: SectionExecution) -> SectionExecution:
        """
        Save or update a SectionExecution in the database.
        """
        existing_section_execution = await self.section_exec_repo.get_by_execution_and_section(section_execution.execution_id, section_execution.section_id)
        if existing_section_execution:
            print("Updating existing section execution")
            existing_section_execution.name = section_execution.name
            existing_section_execution.output = section_execution.output
            existing_section_execution.prompt = section_execution.prompt
            existing_section_execution.order = section_execution.order
            updated_section_execution = await self.section_exec_repo.update(existing_section_execution)
            return updated_section_execution
        else:
            # Add new section execution
            created_section_execution = await self.section_exec_repo.add(section_execution)
            return created_section_execution
        
        
    async def get_by_execution_and_section(self, execution_id: str, section_id: str):
        """
        Retrieve a section execution by execution ID and section ID.
        """
        section_execution = await self.section_exec_repo.get_by_execution_and_section(execution_id, section_id)
        if not section_execution:
            raise ValueError(f"Section execution not found for execution ID {execution_id} and section ID {section_id}")
        return section_execution
        
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
            sections_dict[str(sec_exec.section_id)] = sec_exec.custom_output if sec_exec.custom_output else sec_exec.output
        return sections_dict
