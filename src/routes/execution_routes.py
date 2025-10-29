from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.execution_service import ExecutionService
from src.schemas import ResponseSchema, ModifySection, UpdateLLM
from src.utils import get_transaction_id


router = APIRouter(prefix="/execution")

@router.get("/status/{execution_id}")
async def get_execution_status(execution_id: str, 
                               session: Session = Depends(get_session),
                               transaction_id: str = Depends(get_transaction_id)):
    """
    Get the status of a specific execution.
    """
    try:
        execution_service = ExecutionService(session)
        status = await execution_service.get_execution_status(execution_id)
        if status is None:
            raise HTTPException(
                status_code=404,
                detail=f"Execution with ID {execution_id} not found."
            )
        
        data = {"execution_id": execution_id, "status": status}
        return ResponseSchema(
            transaction_id=transaction_id,
            data=data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while retrieving the execution status: {str(e)}"}
        )
        
@router.delete("/{execution_id}")
async def delete_execution(execution_id: str,
                           session: Session = Depends(get_session),
                           transaction_id: str = Depends(get_transaction_id)):
    """
    Delete an execution by its ID.
    """
    try:
        execution_service = ExecutionService(session)
        await execution_service.delete_execution(execution_id)
        
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"message": f"Execution {execution_id} deleted successfully."}
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
                    "error": f"An error occurred while deleting the execution: {str(e)}"}
        )
        
@router.post("/approve/{execution_id}")
async def approve_execution(execution_id: str,
                            session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
    """
    Approve an execution by its ID.
    """
    try:
        execution_service = ExecutionService(session)
        await execution_service.approve_execution(execution_id)
        
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"message": f"Execution {execution_id} approved successfully."}
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
                    "error": f"An error occurred while approving the execution: {str(e)}"}
        )
        
        
@router.post("/disapprove/{execution_id}")
async def disapprove_execution(execution_id: str,
                                 session: Session = Depends(get_session),
                                 transaction_id: str = Depends(get_transaction_id)):
     """
     Disapprove an execution by its ID.
     """
     try:
          execution_service = ExecutionService(session)
          await execution_service.disapprove_execution(execution_id)
          
          return ResponseSchema(
                transaction_id=transaction_id,
                data={"message": f"Execution {execution_id} disapproved successfully."}
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
                      "error": f"An error occurred while disapproving the execution: {str(e)}"}
          )
        
        
@router.put("/update_llm/{execution_id}")
async def update_llm(execution_id: str,
                     request: UpdateLLM,
                     session: Session = Depends(get_session),
                     transaction_id: str = Depends(get_transaction_id)):
    """
    Update the LLM used for an execution.
    """
    try:
        execution_service = ExecutionService(session)
        updated_execution = await execution_service.update_llm(execution_id, request.llm_id)
        
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(updated_execution)
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
                    "error": f"An error occurred while updating the LLM: {str(e)}"}
        )
        
@router.put("/modify_content/{section_execution_id}")
async def modify_section_content(section_execution_id: str,
                                    request: ModifySection,
                                    session: Session = Depends(get_session),
                                    transaction_id: str = Depends(get_transaction_id)):
        """
        Modify the content of a section execution.
        """
        try:
            execution_service = ExecutionService(session)
            updated_execution = await execution_service.modify_section_exec_content(section_execution_id, request.content)
            
            return ResponseSchema(
                transaction_id=transaction_id,
                data=jsonable_encoder(updated_execution)
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
                        "error": f"An error occurred while modifying the section content: {str(e)}"}
            )
            
            

@router.get("/export_markdown/{execution_id}")
async def export_execution_markdown(execution_id: str, 
                           session: Session = Depends(get_session),
                           transaction_id: str = Depends(get_transaction_id)):
    """
    Export the results of a specific execution as a downloadable markdown file.
    """
    try:
        execution_service = ExecutionService(session)
        export_data = await execution_service.export_execution_markdown(execution_id)
        if not export_data:
            raise HTTPException(
                status_code=404,
                detail=f"No section executions found for execution ID {execution_id}."
            )
        
        # Generar el nombre del archivo
        filename = f"execution_{execution_id}.md"
        
        # Retornar como archivo descargable
        return Response(
            content=export_data,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Transaction-ID": transaction_id  # Mantener el transaction_id en headers
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while exporting the execution: {str(e)}"}
        )
        
@router.get("/export_word/{execution_id}")
async def export_execution_word(execution_id: str,
                            session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
     """
     Export the results of a specific execution as a downloadable Word file.
     """
     try:
          execution_service = ExecutionService(session)
          export_data = await execution_service.export_execution_word(execution_id)
          if not export_data:
                raise HTTPException(
                 status_code=404,
                 detail=f"No section executions found for execution ID {execution_id}."
                )
          
          # Generar el nombre del archivo
          filename = f"execution_{execution_id}.docx"
          
          # Retornar como archivo descargable
          return Response(
                content=export_data,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                 "Content-Disposition": f"attachment; filename={filename}",
                 "X-Transaction-ID": transaction_id  # Mantener el transaction_id en headers
                }
          )
     except Exception as e:
          raise HTTPException(
                status_code=500,
                detail={"transaction_id": transaction_id,
                      "error": f"An error occurred while exporting the execution: {str(e)}"}
          )
          
@router.get("/export_custom_word/{execution_id}")
async def export_execution_custom_word(execution_id: str,
                            session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
     """
     Export the results of a specific execution as a downloadable Word file using a custom template.
     """
     try:
          execution_service = ExecutionService(session)
          export_data = await execution_service.export_custom_word(execution_id)
          if not export_data:
                raise HTTPException(
                 status_code=404,
                 detail=f"No section executions found for execution ID {execution_id}."
                )
          
          # Generar el nombre del archivo
          filename = f"execution_{execution_id}_custom.docx"
          
          # Retornar como archivo descargable
          return Response(
                content=export_data,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                 "Content-Disposition": f"attachment; filename={filename}",
                 "X-Transaction-ID": transaction_id  # Mantener el transaction_id en headers
                }
          )
     except Exception as e:
          raise HTTPException(
                status_code=500,
                detail={"transaction_id": transaction_id,
                      "error": f"An error occurred while exporting the execution with custom template: {str(e)}"}
          )
        
        
@router.get("/{execution_id}")
async def get_execution(execution_id: str, 
                        session: Session = Depends(get_session), 
                        transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve an execution by its ID.
    """
    execution_service = ExecutionService(session)
    try:
        execution = await execution_service.get_execution(execution_id)
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(execution)
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
                    "error": f"An error occurred while retrieving the execution: {str(e)}"}
        )
        
@router.post("/{document_id}")
async def create_execution(document_id: str, 
                           session: Session = Depends(get_session),
                           transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new execution for a document.
    """
    try:
        execution_service = ExecutionService(session)
        execution = await execution_service.create_execution(document_id)
        
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(execution)
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
                    "error": f"An error occurred while creating the execution: {str(e)}"}
        )