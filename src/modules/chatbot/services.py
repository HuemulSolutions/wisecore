from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.execution.service import ExecutionService

class ChatbotServices():
    def __init__(self, session: AsyncSession):
        self.session = session
        
        
    async def get_execution_content(self, execution_id: str) -> str:
        """
        Retrieve the content of an execution by its ID.
        """
        
        execution_content = await ExecutionService(self.session).get_execution(execution_id)
        section_execs = execution_content.section_executions
        if not section_execs:
            raise ValueError(f"No section executions found for execution ID {execution_id}.")
        sorted_execs = sorted(
            section_execs,
            key=lambda x: (x.section.order)
        )
        content = "\n\n-------\n\n".join([i.custom_output if i.custom_output else i.output for i in sorted_execs])
        return content
        
        
    