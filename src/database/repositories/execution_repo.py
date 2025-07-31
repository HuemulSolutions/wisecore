from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from ..models import Execution, Status

class ExecutionRepo(BaseRepository[Execution]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Execution)
        
    async def get_executions_by_doc_id(self, document_id: str)-> list:
        """
        Retrieve all executions for a specific document.
        """
        query = (select(self.model)
                 .where(self.model.document_id == document_id)
                 .order_by(self.model.created_at.desc()))
        result = await self.session.execute(query)
        executions = result.scalars().all()
        return executions if executions else []
    
    async def get_by_id(self, execution_id: str) -> dict:
        """
        Retrieve an execution by its ID with sections and section executions.
        """
        query = (select(self.model)
                 .options(
                     joinedload(self.model.sections_executions).joinedload(Execution.sections_executions.property.mapper.class_.section),
                     joinedload(self.model.document).joinedload(Execution.document.property.mapper.class_.sections)
                 )
                 .where(self.model.id == execution_id))
        result = await self.session.execute(query)
        execution = result.unique().scalar_one_or_none()
        if not execution:
            raise ValueError(f"Execution with ID {execution_id} not found.")
        
        if execution.status == Status.PENDING:
            result_dict = {
                "id": execution.id,
                "document_id": execution.document_id,
                "status": execution.status,
                "created_at": execution.created_at,
                "updated_at": execution.updated_at,
                "document_name": execution.document.name,
                "instruction": execution.user_instruction,
                "sections": [{
                    "id": section.id,
                    "name": section.name,
                    "prompt": section.prompt,
                    "output": "",
                } for section in execution.document.sections]
            }
        else:
            result_dict = {
                "id": execution.id,
                "document_id": execution.document_id,
                "status": execution.status,
                "status_message": execution.status_message,
                "created_at": execution.created_at,
                "updated_at": execution.updated_at,
                "document_name": execution.document.name,
                "instruction": execution.user_instruction,
                "sections": [{
                    "id": section_exec.section.id,
                    "name": section_exec.section.name,
                    "prompt": section_exec.section.prompt,
                    "output": section_exec.output if section_exec.output else None,
                } for section_exec in execution.sections_executions]
            }
        return result_dict
    
    async def get_execution(self, execution_id: str) -> Execution:
        """
        Retrieve an execution by its ID.
        """
        query = select(self.model).where(self.model.id == execution_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def update_status(self, execution_id: str, status: Status, message: str, instructions: str = None) -> Execution:
        """
        Update the status of an execution.
        """
        execution = await self.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution with ID {execution_id} not found.")
        
        execution.status = status
        execution.status_message = message
        if instructions:
            execution.user_instruction = instructions
        await self.session.flush()
        return execution
