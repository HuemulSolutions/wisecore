from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.context_repo import ContextRepo
from src.database.repositories.document_repo import DocumentRepo
from src.database.models import Context, Document
from fastapi import File, UploadFile
import io
from docx2python import docx2python
from PyPDF2 import PdfReader

class ContextService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.context_repo = ContextRepo(session)
        self.document_repo = DocumentRepo(session)
        
    @staticmethod
    def _extract_text_from_docx(file: UploadFile) -> str:
        """
        Extract text from a DOCX file.
        """
        try:
            buf = io.BytesIO(file.file.read())
            doc_result = docx2python(buf)
            content = doc_result.text
        
            lines = []
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    lines.append(line)
            
            return '\n'.join(lines)
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX file '{file.filename}': {str(e)}. Please ensure the file is a valid Word document.")
        
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
            # Validate file before processing
            if not file.filename:
                raise ValueError("No filename provided.")
            
            # Reset file pointer to beginning
            await file.seek(0)
            
            ext = file.filename.split('.')[-1].lower()
            data = await file.read()
            
            if not data:
                raise ValueError(f"File '{file.filename}' is empty.")
            
            text = ""
            if ext in ['txt', 'md']:
                text = data.decode('utf-8', errors='ignore')
            elif ext == "docx":
                # Reset file pointer for docx processing
                await file.seek(0)
                text = self._extract_text_from_docx(file)
            elif ext == "pdf":
                buf = io.BytesIO(data)
                reader = PdfReader(buf)
                pages = [page.extract_text() or "" for page in reader.pages]
                text = "\n".join(pages)
            else:
                raise ValueError(f"Unsupported file type: {ext}. Supported types are: txt, md, docx, pdf.")
            
            if not text.strip():
                raise ValueError(f"No text content could be extracted from file '{file.filename}'.")
                
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