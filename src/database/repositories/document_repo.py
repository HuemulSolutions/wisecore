from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Document, InnerDependency, Section
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

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
        return [
            {
                **doc.__dict__,
                'template_name': doc.template.name if doc.template else None
            }
            for doc in documents
        ]
    
    async def get_by_name(self, name: str) -> Document:
        """
        Retrieve a document by its name.
        """
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, document_id: UUID) -> dict:
        """
        Retrieve a document by its ID with template name and executions info.
        """
        query = (
            select(self.model)
            .options(
                selectinload(Document.template),
                selectinload(Document.executions),
                selectinload(Document.sections)
            )
            .where(self.model.id == document_id)
        )
        result = await self.session.execute(query)
        doc = result.scalar_one_or_none()
        
        if not doc:
            return None
            
        return {
            "id": doc.id,
            "name": doc.name,
            "description": doc.description,
            "template_id": doc.template_id,
            "template_name": doc.template.name if doc.template else None,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "executions": [
                {
                    "id": execution.id,
                    "status": execution.status.value,
                    "status_message": execution.status_message,
                    "created_at": execution.created_at,
                }
                for execution in doc.executions
            ]
        }
    
    async def get_document(self, document_id: UUID) -> Document:
        """
        Retrieve a document by its ID with sections and dependencies.
        """
        query = (
            select(self.model)
            .options(
                selectinload(Document.sections)
                .selectinload(Section.internal_dependencies)
                .selectinload(InnerDependency.depends_on_section_id)
            )
            .where(self.model.id == document_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    