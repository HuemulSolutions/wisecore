from src.database.repositories.dependency_repo import DependencyRepo
from src.database.repositories.document_repo import DocumentRepo
from src.database.models import Dependency
from sqlalchemy.ext.asyncio import AsyncSession


class DependencyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.dependency_repo = DependencyRepo(session)
        self.document_repo = DocumentRepo(session)

    async def get_document_dependencies(self, document_id: str):
        """
        Retrieve all dependencies for a specific document.
        """
        if not await self.document_repo.get_by_id(document_id):
            raise ValueError(f"Document with ID {document_id} not found.")
        
        dependencies = await self.dependency_repo.get_dependencies(document_id)
        return dependencies
        

    async def add_document_dependency(self, document_id: str, depends_on_document_id: str, 
                                      section_id: str = None, depends_on_section_id: str  = None):
        """
        Add a dependency relationship between two full documents or specific sections.
        """
        if not await self.document_repo.get_by_id(document_id):
            raise ValueError(f"Document with ID {document_id} not found.")
        if not await self.document_repo.get_by_id(depends_on_document_id):
            raise ValueError(f"Document with ID {depends_on_document_id} not found.")
        if section_id and not await self.section_repo.get_by_id(section_id):
            raise ValueError(f"Section with ID {section_id} not found in document {document_id}.")
        if depends_on_section_id and not await self.section_repo.get_by_id(depends_on_section_id):
            raise ValueError(f"Section with ID {depends_on_section_id} not found in document {depends_on_document_id}.")
        
        # Create the dependency
        new_dependency = Dependency(
            document_id=document_id,
            section_id=section_id,
            depends_on_document_id=depends_on_document_id,
            depends_on_section_id=depends_on_section_id
        )
        await self.dependency_repo.add(new_dependency)
        return new_dependency
    
    async def delete_document_dependency(self, document_id: str, depends_on_document_id: str):
        """
        Remove a dependency relationship between two documents.
        """
        if not await self.document_repo.get_by_id(document_id):
            raise ValueError(f"Document with ID {document_id} not found.")
        if not await self.document_repo.get_by_id(depends_on_document_id):
            raise ValueError(f"Document with ID {depends_on_document_id} not found.")
        
        # Find and delete the dependency
        dependency = await self.dependency_repo.get_by_ids(document_id, depends_on_document_id)
        if not dependency:
            raise ValueError(f"No dependency found between {document_id} and {depends_on_document_id}.")
        
        await self.dependency_repo.delete(dependency)
        return {"message": "Dependency removed successfully."}
        