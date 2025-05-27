from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Document
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class DocumentRepo(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)
        
    async def get_all_documents(self, limit: int = 100, offset: int = 0):
        """
        Retrieve all documents with optional pagination, including template name.
        """
        query = select(self.model).options(selectinload(Document.template)).limit(limit).offset(offset)
        result = await self.session.execute(query)
        documents = result.scalars().all()
        # Retornar documentos junto con el nombre del template
        return [
            {
                **doc.__dict__,
                'template_name': doc.template.name if doc.template else None
            }
            for doc in documents
        ]
    
