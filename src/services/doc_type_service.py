from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.document_type_repo import DocumentTypeRepo
from src.database.models import DocumentType

class DocumentTypeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.document_type_repo = DocumentTypeRepo(session)
    
    async def get_all_document_types(self) -> list[DocumentType]:
        """
        Retrieve all document types.
        """
        return await self.document_type_repo.get_all()
    
    async def get_document_type_by_id(self, document_type_id: str) -> DocumentType:
        """
        Retrieve a document type by its ID.
        """
        document_type = await self.document_type_repo.get_by_id(document_type_id)
        if not document_type:
            raise ValueError(f"Document type with ID {document_type_id} not found.")
        return document_type
    
    async def create_document_type(self, name: str, color: str) -> DocumentType:
        """
        Create a new document type.
        """
        # Check if document type with same name already exists
        existing_type = await self.document_type_repo.get_by_name(name)
        if existing_type:
            raise ValueError(f"Document type with name '{name}' already exists.")
        
        document_type = DocumentType(
            name=name,
            color=color
        )
        
        return await self.document_type_repo.add(document_type)
    
    async def delete_document_type(self, document_type_id: str) -> None:
        """
        Delete a document type by its ID.
        """
        document_type = await self.document_type_repo.get_by_id(document_type_id)
        if not document_type:
            raise ValueError(f"Document type with ID {document_type_id} not found.")
        
        # Check if there are documents using this type
        if document_type.documents:
            raise ValueError(f"Cannot delete document type '{document_type.name}' because it has associated documents.")
        
        await self.document_type_repo.delete(document_type)