from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.document_repo import DocumentRepo
from src.database.repositories.section_repo import SectionRepo
from src.database.repositories.execution_repo import ExecutionRepo
from src.database.repositories.sectionexec_repo import SectionExecRepo
from src.database.models import Execution, Status, SectionExecution, Section, Document

class GraphServices():
    def __init__(self, session: AsyncSession):
        self.session = session
        self.document_repo = DocumentRepo(session)
        self.section_repo = SectionRepo(session)
        self.execution_repo = ExecutionRepo(session)
        self.section_exec_repo = SectionExecRepo(session)
        
        
    async def init_execution(self, document_id: str, execution_id: str, user_instructions: str = None)-> tuple[Document, list[Section]]:
        
        await self.execution_repo.update_status(execution_id, Status.RUNNING, "Running execution", user_instructions)
        
        document = await self.document_repo.get_document(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        
        sections = await self.section_repo.get_sections_by_doc_id_graph(document_id)
        if not sections:
            raise ValueError(f"No sections found for document with ID {document_id}.")
        return document, sections
    
    
    async def get_document_context(self, document_id: str) -> str:
        """
        Retrieve the document context and dependencies.
        """
        context = await self.document_repo.get_document_context(document_id)
        return context
        

    # async def get_document_by_id(self, document_id: str) -> dict:
    #     """
    #     Get document by ID.
    #     """
    #     async with get_graph_session() as session:
    #         document_repo = DocumentRepo(session)
    #         document = await document_repo.get_by_id(document_id)
    #         if not document:
    #             raise ValueError(f"Document with id {document_id} not found.")
    #         return document
        
    # async def get_section_by_id(self, section_id: str)-> Section:
    #     async with get_graph_session() as session:
    #         section_repo = SectionRepo(session)
    #         document = await section_repo.get_by_id(section_id)
    #         if not document:
    #             raise ValueError(f"Section with id {section_id} not found.")
    #         return document
        
    # async def get_sections_by_document_id(self, document_id: str) -> list:
    #     """
    #     Get sections by document ID.
    #     """
    #     async with get_graph_session() as session:
    #         section_repo = SectionRepo(session)
    #         return await section_repo.get_sections_by_doc_id(document_id)
        
    # async def create_execution(self, document_id: str) -> str:
    #     async with get_graph_session() as session:
    #         execution_repo = ExecutionRepo(session)
    #         new_execution = Execution(
    #             document_id=document_id,
    #             status=Status.PENDING,
    #             status_message="Initializing execution",
    #         )
    #         new_execution = await execution_repo.add(new_execution)
    #         return new_execution.id
        
    async def update_execution(self, execution_id: str, status: Status, status_message: str) -> Execution:
        """
        Update the execution status.
        """
        execution = await self.execution_repo.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution with id {execution_id} not found.")
        execution.status = status
        execution.status_message = status_message
        await self.execution_repo.add(execution)
        return execution
        
    async def save_section_execution(self, section_id: str, execution_id: str, output: str, prompt: str) -> SectionExecution:
        """
        Save the section execution to the database.
        """
        new_section_execution = SectionExecution(
            section_id=section_id,
            execution_id=execution_id,
            output=output,
            custom_output=None,
            prompt=prompt
        )
        await self.section_exec_repo.add(new_section_execution)
        return new_section_execution
        
    # async def update_section_execution(self, section_exec_id: str, output: str) -> SectionExecution:
    #     """
    #     Update the section execution in the database.
    #     """
    #     async with get_graph_session() as session:
    #         section_exec_repo = SectionExecRepo(session)
    #         section_execution = await section_exec_repo.get_by_id(section_exec_id)
    #         if not section_execution:
    #             raise ValueError(f"SectionExecution with id {section_exec_id} not found.")
    #         section_execution.output = output
    #         await section_exec_repo.add(section_execution)
    #         return section_execution


if __name__ == "__main__":
    import asyncio
    from src.database.core import get_graph_session

    async def main():
        async with get_graph_session() as session:
            graph_services = GraphServices(session)
            # Example usage
            document_id = "07bf9e5c-62e9-46a2-b5a3-c0f80f346c44"
            execution_id = "6209ccb1-543f-4d15-adb4-e7cd03ca8e9c"
            sections = await graph_services.init_execution(document_id, execution_id)
            for section in sections:
                print(f"Section ID: {section.id}, Name: {section.name}")
                print(f"Dependencies: {section.dependencies}")

    asyncio.run(main())