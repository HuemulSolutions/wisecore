from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.execution_repo import ExecutionRepo
from src.database.repositories.sectionexec_repo import SectionExecRepo
from src.database.models import Execution, Status


class ExecutionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.execution_repo = ExecutionRepo(session)
        self.section_exec_repo = SectionExecRepo(session)
        
        
    async def get_execution(self, execution_id: str):
        """
        Retrieve an execution by its ID.
        """
        execution = await self.execution_repo.get_by_id(execution_id)
        if not execution:
            raise ValueError(f"Execution with ID {execution_id} not found.")
        return execution

    async def get_executions_by_doc_id(self, document_id: str) -> list:
        """
        Retrieve all executions.
        """
        executions = await self.execution_repo.get_executions_by_doc_id(document_id)
        if not executions:
            raise ValueError("No executions found.")
        return executions
    
    async def create_execution(self, document_id: str):
        """
        Create a new execution for a document.
        """
        
        new_execution = Execution(
            document_id=document_id,
            status=Status.PENDING)
        execution = await self.execution_repo.add(new_execution)
        if not execution:
            raise ValueError(f"Failed to create execution for document ID {document_id}.")
        return execution
    
    async def get_execution_status(self, execution_id: str) -> str:
        """
        Get the status of a specific execution.
        """
        execution = await self.execution_repo.get_by_id(execution_id)
        if not execution:
            raise ValueError(f"Execution with ID {execution_id} not found.")
        return execution.status
    
    async def export_section_execs(self, execution_id: str) -> list:
        """
        Export the section executions for a specific execution.
        """
        section_execs = await self.section_exec_repo.get_sections_by_execution_id(execution_id)
        if not section_execs:
            raise ValueError(f"No section executions found for execution ID {execution_id}.")
        print("results", section_execs)
        sorted_execs = sorted(
            section_execs,
            key=lambda x: (x.section.order)
        )
        export_data = "\n\n-------\n\n".join([i.output for i in sorted_execs])
        return export_data
        