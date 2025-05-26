from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.executions_services import ExecutionService

router = APIRouter(prefix="/execution")

@router.get("/status/{execution_id}")
async def get_execution_status(execution_id: str, session: Session = Depends(get_session)):
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
        
        return {"execution_id": execution_id, "status": status}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving the execution status: {str(e)}"
        )
        
@router.get("/export/{execution_id}")
async def export_execution(execution_id: str, session: Session = Depends(get_session)):
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
        
        return {"execution_id": execution_id, "export_data": export_data}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while exporting the execution: {str(e)}"
        )