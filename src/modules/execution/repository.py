from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from .models import Execution, Status
from src.modules.document.models import Document
import asyncio

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
            "name": execution.name,
            "document_id": execution.document_id,
            "status": execution.status,
            "status_message": execution.status_message,
            "created_at": execution.created_at,
            "updated_at": execution.updated_at,
            "document_name": execution.document.name,
            "instruction": execution.user_instruction,
            "llm_id": execution.model_id
        }
        sorted_section_executions = sorted(execution.sections_executions, key=lambda se: se.order)
        
        sections = []
        for section_exec in sorted_section_executions:
            output = None
            if execution.status in [Status.PENDING, Status.RUNNING]:
                output = ""
            elif section_exec.custom_output:
                output = section_exec.custom_output
            elif section_exec.output:
                output = section_exec.output
            sections.append({
                "id": section_exec.section.id,
                "section_execution_id": section_exec.id,
                "name": section_exec.name,
                "prompt": section_exec.prompt,
                "output": output
            })
        result_dict["sections"] = sections
        return result_dict
    
    async def get_execution(self, execution_id: str, with_model: bool = False) -> Execution:
        """
        Retrieve an execution by its ID.
        """
        query = select(self.model).where(self.model.id == execution_id)
        if with_model:
            query = query.options(joinedload(self.model.model))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def count_executions_by_document_id(self, document_id: str) -> int:
        """
        Count the number of executions for a specific document ID.
        """
        query = select(self.model).where(self.model.document_id == document_id)
        result = await self.session.execute(query)
        executions = result.scalars().all()
        return len(executions)
    
    
    async def get_execution_sections(self, execution_id: str) -> Execution:
        """
        Retrieve all section executions for a specific execution ID.
        """            
        query = (select(self.model)
                 .options(joinedload(self.model.sections_executions))
                 .options(joinedload(self.model.document))
                 .where(self.model.id == execution_id))
        
        result = await self.session.execute(query)
        execution = result.unique().scalar_one_or_none()
        
        if not execution:
            raise ValueError(f"Execution with ID {execution_id} not found.")
        return execution
    
    async def update_status(self, execution_id: str, status: Status, message: str, instructions: str = None) -> Execution:
        """
        Update the status of an execution.
        """
        execution = await self.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution with ID {execution_id} not found.")
        if execution.status == Status.RUNNING and status == Status.PENDING:
            raise ValueError("Cannot change status from RUNNING to PENDING.")
        
        execution.status = status
        execution.status_message = message
        if instructions:
            execution.user_instruction = instructions
        await self.session.flush()
        return execution
    
    
    async def get_execution_to_chunking(self, execution_id: str) -> Execution:
        """
        Retrieve an execution by its ID with the associated section executions
        """
        # Verificar contexto asyncio
        if not asyncio.current_task():
            raise RuntimeError("This method must be called from within an async context")
            
        query = (select(self.model)
                 .options(joinedload(self.model.sections_executions))
                 .where(self.model.id == execution_id))
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_approved_execution_by_doc_id(self, document_id: str) -> Execution:
        """
        Retrieve the latest approved execution for a specific document.
        """
        query = (select(self.model)
                 .where(self.model.document_id == document_id, self.model.status == Status.APPROVED)
                 .order_by(self.model.created_at.desc()))
        result = await self.session.execute(query)
        return result.scalars().first()

    async def check_if_document_exists(self, document_id: str) -> Execution:
        """
        Check if a document exists by its ID.
        """
        query = select(Document).where(Document.id == document_id)
        result = await self.session.execute(query)
        document = result.scalar_one_or_none()
        return document