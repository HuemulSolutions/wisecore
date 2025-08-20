from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.document_service import DocumentService
from src.services.execution_service import ExecutionService
from src.services.context_service import ContextService
from src.services.dependency_service import DependencyService
from src.services.document_section_service import SectionService
from src.utils import get_transaction_id
from src.schemas import (ResponseSchema, CreateDocument, 
                         CreateDocumentDependency, CreateDocumentSection,
                         AddDocumentContextText)

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
        
@router.delete("/{document_id}")
async def delete_document(document_id: str,
                            session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
        """
        Delete a document by its ID.
        """
        document_service = DocumentService(session)
        try:
            await document_service.delete_document(document_id)
            return ResponseSchema(
                transaction_id=transaction_id,
                data={"message": "Document deleted successfully"}
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
                        "error": f"An error occurred while deleting the document: {str(e)}"}
            )
        
@router.get("/")
async def get_all_documents(organization_id: str = None, 
                            session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all documents.
    """
    document_service = DocumentService(session)
    try:
        documents = await document_service.get_all_documents(organization_id)
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
            organization_id=create_document.organization_id,
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
        
        
@router.get("/{document_id}/dependencies")
async def get_document_dependencies(document_id: str,
                                    session: Session = Depends(get_session),
                                    transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all dependencies for a specific document.
    """
    document_service = DependencyService(session)
    try:
        dependencies = await document_service.get_document_dependencies(document_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(dependencies)
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
                    "error": f"An error occurred while retrieving dependencies for document ID {document_id}: {str(e)}"}
        )
        
        
@router.post("/{document_id}/dependencies")
async def add_document_dependency(document_id: str,
                                  document_dependency: CreateDocumentDependency,
                                  session: Session = Depends(get_session),
                                  transaction_id: str = Depends(get_transaction_id)):
    """
    Add a dependency relationship between two documents.
    
    Args:
        document_id: The ID of the document that depends on another
        depends_on_id: The ID of the document that is depended upon
    """
    document_service = DependencyService(session)
    try:
        dependency = await document_service.add_document_dependency(
            document_id=document_id,
            depends_on_document_id=document_dependency.depends_on_document_id,
            section_id=document_dependency.section_id,
            depends_on_section_id=document_dependency.depends_on_section_id
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(dependency)
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
        
@router.delete("/{document_id}/dependencies/{dependency_id}")
async def delete_document_dependency(document_id: str,
                                     dependency_id: str,
                                     session: Session = Depends(get_session),
                                     transaction_id: str = Depends(get_transaction_id)):
    """
    Delete a dependency relationship between two documents.
    
    Args:
        document_id: The ID of the document that has the dependency
        dependency_id: The ID of the dependency to be deleted
    """
    dependency_service = DependencyService(session)
    try:
        await dependency_service.delete_document_dependency(document_id, dependency_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"message": "Dependency deleted successfully"}
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
                    "error": f"An error occurred while deleting dependency: {str(e)}"}
        )
        
@router.get("/{document_id}/context")
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
        

@router.get("/{document_id}/executions")
async def get_executions_by_doc_id(document_id: str,
                                   session: Session = Depends(get_session),
                                   transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all executions for a document.
    """
    try:
        execution_service = ExecutionService(session)
        executions = await execution_service.get_executions_by_doc_id(document_id)
        
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(executions)
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
                    "error": f"An error occurred while retrieving executions: {str(e)}"}
        )
        
        
@router.post("/{document_id}/add_context_text")
async def add_context_to_document(document_id: str,
                                    context: AddDocumentContextText,
                                    session: Session = Depends(get_session),
                                    transaction_id: str = Depends(get_transaction_id)):
    """ Add context text to a document.
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
        
@router.post("/{document_id}/add_context_file")
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
          
@router.delete("/{document_id}/context/{context_id}")
async def delete_document_context(document_id: str,
                                    context_id: str,
                                    session: Session = Depends(get_session),
                                    transaction_id: str = Depends(get_transaction_id)):
        """
        Delete a context from a document.
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