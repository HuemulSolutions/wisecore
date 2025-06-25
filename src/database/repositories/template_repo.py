from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models import Template, TemplateSection

class TemplateRepo(BaseRepository[Template]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Template)
        
    async def get_by_id(self, template_id: str) -> Template:
        """
        Retrieve a template by its ID and template sections.
        """
        query = (select(self.model)
                 .where(self.model.id == template_id)
                 .options(selectinload(Template.template_sections)))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()