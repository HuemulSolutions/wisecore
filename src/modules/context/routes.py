from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from .service import ContextService
from src.utils import get_transaction_id
from src.schemas import ResponseSchema
from .schemas import AddDocumentContextText

router = APIRouter(prefix="/context")

@router.get("/{document_id}")
async def get_document_context(document_id: str,
                               session: Session = Depends(get_session),
                               transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all context for a specific document.
    """
    context_service = ContextService(session)
    try:
        context = await context_service.get_context_by_document_id(document_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(context)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail={"transaction_id": transaction_id,
                    "error": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while retrieving context for document ID {document_id}: {str(e)}"}
        )

@router.post("/{document_id}/text")
async def add_context_text_to_document(document_id: str,
                                       context: AddDocumentContextText,
                                       session: Session = Depends(get_session),
                                       transaction_id: str = Depends(get_transaction_id)):
    """
    Add context text to a document.
    """
    context_service = ContextService(session)
    try:
        new_context = await context_service.add_context_to_document(
            document_id=document_id,
            name=context.name,
            content=context.content
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(new_context)
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
                    "error": f"An error occurred while adding context to the document: {str(e)}"}
        )

@router.post("/{document_id}/file")
async def add_context_file_to_document(document_id: str,
                                       file: UploadFile = File(...),
                                       session: Session = Depends(get_session),
                                       transaction_id: str = Depends(get_transaction_id)):
    """
    Add context file to a document.
    """
    context_service = ContextService(session)
    try:
        new_context = await context_service.add_context_to_document(
            document_id=document_id,
            name=file.filename,
            file=file
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(new_context)
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
                    "error": f"An error occurred while adding context file to the document: {str(e)}"}
        )

@router.delete("/{context_id}")
async def delete_context(context_id: str,
                         session: Session = Depends(get_session),
                         transaction_id: str = Depends(get_transaction_id)):
    """
    Delete a context by its ID.
    """
    context_service = ContextService(session)
    try:
        await context_service.delete_context(context_id=context_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"message": "Context deleted successfully"}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail={"transaction_id": transaction_id,
                    "error": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while deleting context: {str(e)}"}
        )
