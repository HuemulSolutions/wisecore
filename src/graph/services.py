from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.document_repo import DocumentRepo
from src.database.repositories.section_repo import SectionRepo
from src.database.repositories.execution_repo import ExecutionRepo
from src.database.repositories.knowledge_repo import KnowledgeRepo
from src.database.repositories.sectionexec_repo import SectionExecRepo
from src.database.models import Execution, Status, SectionExecution, Section
from src.database.core import get_graph_session

class GraphServices():
    
    async def get_document_by_id(self, document_id: str) -> dict:
        """
        Get document by ID.
        """
        async with get_graph_session() as session:
            document_repo = DocumentRepo(session)
            document = await document_repo.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document with id {document_id} not found.")
            return document
        
    async def get_section_by_id(self, section_id: str)-> Section:
        async with get_graph_session() as session:
            section_repo = SectionRepo(session)
            document = await section_repo.get_by_id(section_id)
            if not document:
                raise ValueError(f"Section with id {section_id} not found.")
            return document
        
    async def get_sections_by_document_id(self, document_id: str) -> list:
        """
        Get sections by document ID.
        """
        async with get_graph_session() as session:
            section_repo = SectionRepo(session)
            return await section_repo.get_sections_by_doc_id(document_id)
        
    async def create_execution(self, document_id: str) -> str:
        async with get_graph_session() as session:
            execution_repo = ExecutionRepo(session)
            new_execution = Execution(
                document_id=document_id,
                status=Status.PENDING,
                status_message="Initializing execution",
            )
            new_execution = await execution_repo.add(new_execution)
            return new_execution.id
        
    async def update_execution(self, execution_id: str, status: str, status_message: str) -> Execution:
        """
        Update the execution status.
        """
        if status not in [item.value for item in Status]:
            raise ValueError(f"Invalid status: {status}")
        
        async with get_graph_session() as session:
            execution_repo = ExecutionRepo(session)
            execution = await execution_repo.get_by_id(execution_id)
            if not execution:
                raise ValueError(f"Execution with id {execution_id} not found.")
            execution.status = Status(status)
            execution.status_message = status_message
            await execution_repo.add(execution)
            return execution
        
    async def get_dependecies(self, section_id: str) -> str:
        """
        Get dependencies for a section.
        """
        async with get_graph_session() as session:
            section_repo = SectionRepo(session)
            dependencies = await section_repo.get_dependencies(section_id)
            dependencies_list = []
            for dependency in dependencies:
                if dependency.type.value == "section":
                    section_exec_repo = SectionExecRepo(session)
                    section_exec = await section_exec_repo.get_last_execution(dependency.depends_on)
                    dependencies_list.append(
                        {
                            "id": section_exec.id,
                            "content": section_exec.output,
                            "type": "section",
                        }
                    )
                else:
                    knowledge_repo = KnowledgeRepo(session)
                    content = await knowledge_repo.get_by_id(dependency.depends_on)
                    dependencies_list.append(
                        {
                            "id": content.id,
                            "content": content.content,
                            "type": "knowledge",
                        }
                    )
            return dependencies_list
        
    async def save_section_execution(self, section_id: str, execution_id: str, output: str) -> SectionExecution:
        """
        Save the section execution to the database.
        """
        async with get_graph_session() as session:
            section_exec_repo = SectionExecRepo(session)
            new_section_execution = SectionExecution(
                section_id=section_id,
                execution_id=execution_id,
                output=output,
            )
            await section_exec_repo.add(new_section_execution)
            return new_section_execution

        