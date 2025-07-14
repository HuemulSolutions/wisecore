from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models import Section, Document, SectionExecution, InnerDependency

class SectionRepo(BaseRepository[Section]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Section)
        
    async def get_sections_by_doc_id(self, document_id: str) -> list[Section]:
        
        sections = await self.session.execute(
            select(Section)
            .options(selectinload(Section.internal_dependencies)
                .selectinload(InnerDependency.depends_on_section),)
            .where(Section.document_id == document_id)
            .order_by(Section.order)
        )
        sections = sections.scalars().all()
        
        if sections:
            for section in sections:
                section.dependencies = [dep.depends_on_section.name for dep in section.internal_dependencies]
        else:
            sections = []
            
        return sections
    
    async def get_by_name_and_document_id(self, name: str, document_id: str) -> Section | None:
        result = await self.session.execute(
            select(Section).where(
                Section.name == name,
                Section.document_id == document_id
            )
        )
        return result.scalar_one_or_none()
    
    
    async def get_by_order_and_document_id(self, order: int, document_id: str) -> Section | None:
        result = await self.session.execute(
            select(Section).where(
                Section.order == order,
                Section.document_id == document_id
            )
        )
        return result.scalar_one_or_none()
    
    
        