from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.document_service import DocumentService
from src.utils import get_transaction_id
from src.schemas import ResponseSchema, CreateDocument

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
        
@router.post("/")
async def create_document(create_document: CreateDocument,
                          session: Session = Depends(get_session),
                          transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new document.
    """
    document_service = DocumentService(session)
    try:
        new_document = await document_service.create_document(
            name=create_document.name,
            description=create_document.description,
            template_id=create_document.template_id
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(new_document)
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
                    "error": f"An error occurred while creating the document: {str(e)}"}
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
        
@router.post("/{document_id}/dependencies/{depends_on_id}")
async def add_document_dependency(document_id: str,
                                  depends_on_id: str,
                                  session: Session = Depends(get_session),
                                  transaction_id: str = Depends(get_transaction_id)):
    """
    Add a dependency relationship between two documents.
    
    Args:
        document_id: The ID of the document that depends on another
        depends_on_id: The ID of the document that is depended upon
    """
    document_service = DocumentService(session)
    try:
        updated_document = await document_service.add_document_dependency(document_id, depends_on_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(updated_document)
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
                    "error": f"An error occurred while adding dependency: {str(e)}"}
        )