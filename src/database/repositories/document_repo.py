from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Document, Dependency
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
        return [
            {
                **doc.__dict__,
                'template_name': doc.template.name if doc.template else None
            }
            for doc in documents
        ]
    
    async def add_dependency(self, document_id: str, depends_on_id: str):
        """
        Add a dependency relationship between two documents.
        
        Args:
            document_id: The ID of the document that depends on another
            depends_on_id: The ID of the document that is depended upon
        """
        # Verify both documents exist
        document = await self.get_by_id(document_id)
        depends_on_document = await self.get_by_id(depends_on_id)
        
        if not document or not depends_on_document:
            raise ValueError("One or both documents not found")
        
        # Check if dependency already exists
        existing_dependency = await self.session.execute(
            select(Dependency).where(
                Dependency.document_id == document_id,
                Dependency.depends_on_id == depends_on_id
            )
        )
        if existing_dependency.scalar_one_or_none():
            raise ValueError("Dependency already exists")
        
        # Create the dependency
        dependency = Dependency(
            document_id=document_id,
            depends_on_id=depends_on_id
        )
        
        self.session.add(dependency)
        await self.session.commit()
        
        return dependency
    
    async def remove_dependency(self, document_id: str, depends_on_id: str):
        """
        Remove a dependency relationship between two documents.
        
        Args:
            document_id: The ID of the document that depends on another
            depends_on_id: The ID of the document that is depended upon
        """
        dependency = await self.session.execute(
            select(Dependency).where(
                Dependency.document_id == document_id,
                Dependency.depends_on_id == depends_on_id
            )
        )
        dependency_obj = dependency.scalar_one_or_none()
        
        if not dependency_obj:
            raise ValueError("Dependency not found")
        
        await self.session.delete(dependency_obj)
        await self.session.commit()
        
        return True
    
    async def get_document_dependencies(self, document_id: str):
        """
        Get all documents that the specified document depends on.
        """
        document = await self.session.execute(
            select(Document)
            .options(selectinload(Document.outgoing_dependencies).selectinload(Dependency.depends_on))
            .where(Document.id == document_id)
        )
        doc = document.scalar_one_or_none()
        
        if not doc:
            raise ValueError("Document not found")
        
        return [dep.depends_on for dep in doc.outgoing_dependencies]
    
    async def get_document_dependents(self, document_id: str):
        """
        Get all documents that depend on the specified document.
        """
        document = await self.session.execute(
            select(Document)
            .options(selectinload(Document.incoming_dependencies).selectinload(Dependency.document))
            .where(Document.id == document_id)
        )
        doc = document.scalar_one_or_none()
        
        if not doc:
            raise ValueError("Document not found")
        
        return [dep.document for dep in doc.incoming_dependencies]

