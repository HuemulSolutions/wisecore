from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import TemplateSection

class TemplateSectionRepo(BaseRepository[TemplateSection]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TemplateSection)