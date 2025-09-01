from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.doc_type_service import DocumentTypeService
from src.schemas import ResponseSchema, CreateDocumentType
from src.utils import get_transaction_id

router = APIRouter(prefix="/document_types")

@router.get("/")
async def get_all_document_types(session: Session = Depends(get_session),
                                transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all document types.
    """
    document_type_service = DocumentTypeService(session)
    try:
        document_types = await document_type_service.get_all_document_types()
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(document_types)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while retrieving document types: {str(e)}"}
        )

@router.get("/{document_type_id}")
async def get_document_type(document_type_id: str,
                           session: Session = Depends(get_session),
                           transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve a document type by its ID.
    """
    document_type_service = DocumentTypeService(session)
    try:
        document_type = await document_type_service.get_document_type_by_id(document_type_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(document_type)
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
                    "error": f"An error occurred while retrieving the document type: {str(e)}"}
        )

@router.post("/")
async def create_document_type(document_type: CreateDocumentType,
                              session: Session = Depends(get_session),
                              transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new document type.
    """
    document_type_service = DocumentTypeService(session)
    try:
        new_document_type = await document_type_service.create_document_type(
            name=document_type.name,
            color=document_type.color
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(new_document_type)
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
                    "error": f"An error occurred while creating the document type: {str(e)}"}
        )

@router.delete("/{document_type_id}")
async def delete_document_type(document_type_id: str,
                              session: Session = Depends(get_session),
                              transaction_id: str = Depends(get_transaction_id)):
    """
    Delete a document type by its ID.
    """
    document_type_service = DocumentTypeService(session)
    try:
        await document_type_service.delete_document_type(document_type_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"message": f"Document type with ID {document_type_id} has been deleted successfully"}
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
                    "error": f"An error occurred while deleting the document type: {str(e)}"}
        )