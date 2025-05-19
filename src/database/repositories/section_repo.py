from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Section, Document

class SectionRepo(BaseRepository[Section]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Section)
        
    async def get_sections_by_doc_id(self, document_id: str) -> list[Section]:
        template_id = await self.session.execute(
            select(Document.template_id).where(Document.id == document_id)
        )
        template_id = template_id.scalar_one_or_none()
        if template_id is None:
            raise ValueError(f"Document with id {document_id} not found.")
        
        sections = await self.session.execute(
            select(Section).where(Section.template_id == template_id)
        )
        return sections.scalars().all()