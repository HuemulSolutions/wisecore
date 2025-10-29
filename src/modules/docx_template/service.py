from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from src.database.repositories.docx_template_repo import DocxTemplateRepo
from src.modules.document.service import DocumentService
from src.database.models import DocxTemplate


class DocxTemplateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.docx_template_repo = DocxTemplateRepo(session)
        
    async def upload_docx_template(self, document_id: str, file: UploadFile) -> DocxTemplate:
        """
        Store or update a DOCX template associated to a document.
        """
        if not file:
            raise ValueError("No file provided.")

        if not file.filename:
            raise ValueError("Uploaded file must have a filename.")

        if not file.filename.lower().endswith(".docx"):
            raise ValueError("Only .docx files are supported.")

        document = await DocumentService(self.session).get_document_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")

        await file.seek(0)
        file_bytes = await file.read()
        if not file_bytes:
            raise ValueError(f"File '{file.filename}' is empty.")

        file_name = file.filename
        template_name = file_name.rsplit(".", 1)[0]
        mime_type = file.content_type or "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        file_size = len(file_bytes)

        print("Obtaining existing template...")
        existing_template = await self.docx_template_repo.get_by_document_id(document_id)

        if existing_template:
            existing_template.name = template_name
            existing_template.file_name = file_name
            existing_template.mime_type = mime_type
            existing_template.file_size = file_size
            existing_template.file_data = file_bytes
            print("Updating existing template...")
            updated_template = await self.docx_template_repo.update(existing_template)
            return updated_template

        new_template = DocxTemplate(
            name=template_name,
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size,
            file_data=file_bytes,
            document_id=document_id
        )
        new_template = await self.docx_template_repo.add(new_template)
        return new_template
    
    async def get_by_document_id(self, document_id: str) -> DocxTemplate:
        """
        Retrieve the DOCX template associated with a document.
        """
        template = await self.docx_template_repo.get_by_document_id(document_id)
        if not template:
            raise ValueError(f"No DOCX template found for document with ID {document_id}.")
        return template
    
