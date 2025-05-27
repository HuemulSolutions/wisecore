from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.document_service import DocumentService
from src.utils import get_transaction_id
from src.schemas import ResponseSchema

router = APIRouter(prefix="/documents")

@router.get("/{document_id}")
async def get_document(document_id: str, 
                       session: Session = Depends(get_session), 
                       transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve a document by its ID.
    """
    docuemnt_service = DocumentService(session)
    try:
        document = await docuemnt_service.get_document_by_id(document_id)
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(document)
        )
        return response
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
                    "error": f"An error occurred while retrieving the document: {str(e)}"}
        )
        
@router.get("/")
async def get_all_documents(session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all documents.
    """
    document_service = DocumentService(session)
    try:
        documents = await document_service.get_all_documents()
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(documents)
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
                    "error": f"An error occurred while retrieving all documents: {str(e)}"}
        )
        
@router.get("/{document_id}/sections")
async def get_document_sections(document_id: str,
                                session: Session = Depends(get_session),
                                transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all sections for a specific document.
    """
    document_service = DocumentService(session)
    try:
        sections = await document_service.get_document_sections(document_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(sections)
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
                    "error": f"An error occurred while retrieving sections for document ID {document_id}: {str(e)}"}
        )