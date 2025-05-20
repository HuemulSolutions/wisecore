from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import SectionExecution
from sqlalchemy.future import select

class SectionExecRepo(BaseRepository[SectionExecution]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SectionExecution)

    async def get_last_execution(self, section_id: str) -> str:
        section_execution = await self.session.execute(
            select(SectionExecution)
            .where(SectionExecution.section_id == section_id)
            .order_by(SectionExecution.created_at.desc())
        )
        section_execution = section_execution.scalars().first()
        if section_execution is None:
            raise ValueError(f"No execution found for section with id {section_id}.")
        return section_execution.output