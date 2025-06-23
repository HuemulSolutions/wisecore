from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Template

class TemplateRepo(BaseRepository[Template]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Template)