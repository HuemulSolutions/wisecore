from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.execution.service import ExecutionService
from src.modules.llm.service import LLMService

class ChatbotServices():
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm_service = LLMService(session)
        
        
    async def get_execution_content(self, execution_id: str) -> str:
        """
        Retrieve the content of an execution by its ID.
        """
        
        section_execs = await ExecutionService(self.session).get_sections_by_execution_id(execution_id)
        if not section_execs:
            raise ValueError(f"No section executions found for execution ID {execution_id}.")
        sorted_execs = sorted(
            section_execs,
            key=lambda x: (x.order)
        )
        content = "\n\n-------\n\n".join([i.custom_output if i.custom_output else i.output for i in sorted_execs])
        return content
        
    async def get_llm(self):
        """
        Retrieve the default LLM model.
        """
        llm = await self.llm_service.get_model()
        return llm
        
    