from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.execution_service import ExecutionService
from src.schemas import ResponseSchema
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
        
@router.get("/export/{execution_id}")
async def export_execution(execution_id: str, 
                           session: Session = Depends(get_session),
                           transaction_id: str = Depends(get_transaction_id)):
    """
    Export the results of a specific execution.
    """
    try:
        execution_service = ExecutionService(session)
        export_data = await execution_service.export_section_execs(execution_id)
        if not export_data:
            raise HTTPException(
                status_code=404,
                detail=f"No section executions found for execution ID {execution_id}."
            )
        data = {"execution_id": execution_id, "export_data": export_data}
        return ResponseSchema(
            transaction_id=transaction_id,
            data=data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while exporting the execution: {str(e)}"}
        )