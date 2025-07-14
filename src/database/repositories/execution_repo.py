from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from ..models import Execution

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
        
        result_dict = {
            "id": execution.id,
            "document_id": execution.document_id,
            "status": execution.status,
            "created_at": execution.created_at,
            "updated_at": execution.updated_at,
            "document_name": execution.document.name,
            "sections_executions": [{
                "id": section_exec.section.id,
                "output": section_exec.output,
                "custom_output": section_exec.custom_output,
            } for section_exec in execution.sections_executions],
            "sections": [{
                "id": section.id,
                "name": section.name,
                "prompt": section.prompt,
            } for section in execution.document.sections]
            
        }
        return result_dict
