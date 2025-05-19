from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Document

class DocumentRepo(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)
