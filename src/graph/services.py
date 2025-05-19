from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.document_repo import DocumentRepo
from src.database.repositories.section_repo import SectionRepo
from src.database.repositories.execution_repo import ExecutionRepo
from src.database.models import Execution
from src.database.core import get_graph_session

class GraphServices():
        
    async def get_sections_by_document_id(self, document_id: int):
        """
        Get sections by document ID.
        """
        async with get_graph_session() as session:
            section_repo = SectionRepo(session)
            return await section_repo.get_sections_by_doc_id(document_id)
        
    async def create_execution(self, document_id: str):
        async with get_graph_session() as session:
            execution_repo = ExecutionRepo(session)
            new_execution = Execution(
                document_id=document_id,
                status="pending",
                status_message="Initializing execution",
            )
            new_execution = await execution_repo.add(new_execution)
            return new_execution.id
        