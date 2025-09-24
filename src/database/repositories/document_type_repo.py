from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import DocumentType

class DocumentTypeRepo(BaseRepository[DocumentType]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DocumentType)
        
    async def get_all(self, organization_id: str) -> list[DocumentType]:
        """
        Retrieve all document types for a specific organization.
        """
        query = select(self.model).where(self.model.organization_id == organization_id)
        result = await self.session.execute(query)
        document_types = result.scalars().all()
        return document_types
        
    async def get_by_name(self, name: str, organization_id: str) -> DocumentType:
        """
        Retrieve a document type by its name.
        """
        query = select(self.model).where(self.model.name == name, self.model.organization_id == organization_id)
        result = await self.session.execute(query)
        document_type = result.scalars().one_or_none()
        return document_type
