from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.section_execution_service import SectionExecutionService
from src.schemas import ResponseSchema
from src.utils import get_transaction_id


router = APIRouter(prefix="/section_executions")


@router.delete("/{section_execution_id}")
async def delete_section_execution(section_execution_id: str,
                                   session: Session = Depends(get_session),
                                   transaction_id: str = Depends(get_transaction_id)):
    """
    Delete a section execution by its ID.
    """
    try:
        section_execution_service = SectionExecutionService(session)
        await section_execution_service.delete_section_execution(section_execution_id)
        
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"message": f"Section execution {section_execution_id} deleted successfully."}
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
                    "error": f"An error occurred while deleting the section execution: {str(e)}"}
        )
