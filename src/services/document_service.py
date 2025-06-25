from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.document_repo import DocumentRepo
from src.database.repositories.section_repo import SectionRepo

class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.document_repo = DocumentRepo(session)
        self.section_repo = SectionRepo(session)

    async def get_document_by_id(self, document_id: str):
        """
        Retrieve a document by its ID.
        """
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        return document
    
    async def get_all_documents(self):
        """
        Retrieve all documents.
        """
        documents = await self.document_repo.get_all_documents()
        return documents
    
    async def get_document_sections(self, document_id: str):
        """
        Retrieve all sections for a specific document.
        """
        sections = await self.section_repo.get_sections_by_doc_id(document_id)
        if not sections:
            raise ValueError(f"No sections found for document ID {document_id}.")
        return sections
