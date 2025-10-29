from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.modules.docx_template.service import DocxTemplateService
from src.database.core import get_session
from src.schemas import ResponseSchema
from src.utils import get_transaction_id
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/docx_template", tags=["DocxTemplate"])

@router.post("/{document_id}")
async def upload_docx_template(document_id: str,
                               file: UploadFile = File(...),
                               session: Session = Depends(get_session),
                               transaction_id: str = Depends(get_transaction_id)):
    """
    Upload or replace the DOCX template associated with a document.
    """
    docx_template_service = DocxTemplateService(session)
    try:
        template = await docx_template_service.upload_docx_template(
            document_id=document_id,
            file=file,
        )
        template_payload = jsonable_encoder({
            "id": template.id,
            "name": template.name,
            "file_name": template.file_name,
            "mime_type": template.mime_type,
            "file_size": template.file_size,
            "document_id": template.document_id,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
        })
        return ResponseSchema(
            transaction_id=transaction_id,
            data=template_payload
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id,
                    "error": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while uploading the DOCX template: {str(e)}"}
        )