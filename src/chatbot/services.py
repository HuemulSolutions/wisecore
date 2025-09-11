from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.sectionexec_repo import SectionExecRepo

class ChatbotServices():
    def __init__(self, session: AsyncSession):
        self.session = session
        self.section_exec_repo = SectionExecRepo(session)
        
        
    async def get_execution_content(self, execution_id: str) -> str:
        """
        Retrieve the content of an execution by its ID.
        """
        
        section_execs = await self.section_exec_repo.get_sections_by_execution_id(execution_id)
        if not section_execs:
            raise ValueError(f"Section execution with ID {execution_id} not found.")
        
        if not section_execs:
            raise ValueError(f"No section executions found for execution ID {execution_id}.")
        sorted_execs = sorted(
            section_execs,
            key=lambda x: (x.section.order)
        )
        content = "\n\n-------\n\n".join([i.custom_output if i.custom_output else i.output for i in sorted_execs])
        return content
        
        
    