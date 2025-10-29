from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import DocxTemplate

class DocxTemplateRepo(BaseRepository[DocxTemplate]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DocxTemplate)
        
    async def get_by_document_id(self, document_id: str):
        """
        Retrieve DocxTemplate by document ID.
        """
        query = select(self.model).where(self.model.document_id == document_id)
        result = await self.session.execute(query)
        return result.scalars().first()

