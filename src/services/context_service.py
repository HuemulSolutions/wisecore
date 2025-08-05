from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.context_repo import ContextRepo
from src.database.repositories.document_repo import DocumentRepo
from src.database.models import Context, Document
from fastapi import File, UploadFile
import io
from docx import Document as DocxDocument
from PyPDF2 import PdfReader

class ContextService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.context_repo = ContextRepo(session)
        self.document_repo = DocumentRepo(session)
        
    async def get_context_by_document_id(self, document_id: str):
        """
        Retrieve context by document ID.
        """
        context = await self.context_repo.get_by_document_id(document_id)
        if not context:
            return []
        return context
        
    async def add_context_to_document(self, document_id: str, name: str, content: str = None, file: UploadFile = None):
        """
        Add context text to a document.
        """
        if not await self.document_repo.get_by_id(document_id):
            raise ValueError(f"Document with ID {document_id} not found.")
        
        if content:
            new_context = Context(name=name, content=content, document_id=document_id)
        elif file:
            ext = file.filename.split('.')[-1]
            data = await file.read()
            text = ""
            if ext in ['txt', 'md']:
                text = data.decode('utf-8', errors='ignore')
            elif ext == "docx":
                buf = io.BytesIO(data)
                doc = DocxDocument(buf)
                text = "\n".join([para.text for para in doc.paragraphs])
            elif ext == "pdf":
                buf = io.BytesIO(data)
                reader = PdfReader(buf)
                pages = [page.extract_text() or "" for page in reader.pages]
                text = "\n".join(pages)
            else:
                raise ValueError(f"Unsupported file type: {ext}. Supported types are: txt, md, docx, pdf.")
            new_context = Context(name=name, content=text, document_id=document_id)
        
        new_context = await self.context_repo.add(new_context)
        return new_context
    
    async def delete_context(self, context_id: str):
        """
        Delete a context by its ID.
        """
        context = await self.context_repo.get_by_id(context_id)
        if not context:
            raise ValueError(f"Context with ID {context_id} not found.")
        
        await self.context_repo.delete(context)
        return {"message": "Context deleted successfully."}