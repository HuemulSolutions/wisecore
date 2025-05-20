from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import KnowledgeBase

class KnowledgeRepo(BaseRepository[KnowledgeBase]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, KnowledgeBase)