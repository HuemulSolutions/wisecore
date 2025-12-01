from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.document.service import DocumentService
from src.modules.section.service import SectionService
from src.modules.execution.service import ExecutionService
from src.modules.section_execution.service import SectionExecutionService
from src.modules.llm.service import LLMService
from src.modules.execution.models import Status, Execution
from src.modules.section.models import Section
from src.modules.document.models import Document
from src.modules.section_execution.models import SectionExecution

class GraphServices():
    def __init__(self, session: AsyncSession):
        self.session = session
        self.document_service = DocumentService(session)
        self.section_service = SectionService(session)
        self.execution_service = ExecutionService(session)
        self.llm_service = LLMService(session)
        self.section_exec_service = SectionExecutionService(session)
        
        
    async def init_execution(self, document_id: str, execution_id: str, user_instructions: str = None)-> tuple[Document, list[Section]]:
        
        await self.execution_service.update_status(execution_id, Status.RUNNING, "Running execution", user_instructions)
        
        document = await self.document_service.get_document(document_id)
        
        sections = await self.section_service.get_document_sections_graph(document_id)
        if not sections:
            raise ValueError(f"No sections found for document with ID {document_id}.")
        
        return document, sections
    

    
    async def get_llm(self, llm_id: str) -> str:
        """
        Retrieve the LLM name used in the execution.
        """
        llm_name = await self.llm_service.get_model(llm_id)
        return llm_name
    
    
    async def get_document_context(self, document_id: str) -> str:
        """
        Retrieve the document context and dependencies.
        """
        context = await self.document_service.get_document_context(document_id)
        return context
        
    async def update_execution(self, execution_id: str, status: Status, status_message: str) -> Execution:
        """
        Update the execution status.
        """
        return await self.execution_service.update_status(execution_id, status, status_message)
        
    async def save_section_execution(self, section_id: str, name: str, execution_id: str, output: str, prompt: str, order: int) -> SectionExecution:
        """
        Save the section execution to the database.
        """
        new_section_execution = SectionExecution(
            name=name,
            section_id=section_id,
            execution_id=execution_id,
            output=output,
            custom_output=None,
            prompt=prompt,
            order=order
        )
        await self.section_exec_service.save_or_update_section_execution(new_section_execution)
        return new_section_execution
    
    async def get_partial_sections_execution(self, exec_id: str) -> dict:
        """
        Get the output of a section execution.
        """
        execution = await self.execution_service.check_execution_exists(exec_id)
        if not execution:
            raise ValueError(f"Execution with ID {exec_id} does not exist.")
        sections = await self.section_exec_service.get_partial_section_execution_by_id(exec_id)
        return sections

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