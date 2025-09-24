from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import TemplateSectionDependency
from sqlalchemy.future import select

class TemplateSectionDepRepo(BaseRepository[TemplateSectionDependency]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TemplateSectionDependency)