from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from .service import SectionExecutionService
from .schemas import ModifySectionExecutionSchema, AddSectionExecutionSchema
from src.schemas import ResponseSchema
from src.utils import get_transaction_id


router = APIRouter(prefix="/section_executions")


@router.post("/{execution_id}")
async def add_section_execution(execution_id: str,
                                request: AddSectionExecutionSchema,
                                session: Session = Depends(get_session),
                                transaction_id: str = Depends(get_transaction_id)):
    """
    Add a new section execution to an execution.
    """
    try:
        section_execution_service = SectionExecutionService(session)
        new_section_execution = await section_execution_service.add_section_execution_to_execution(
            execution_id=execution_id,
            name=request.name,
            output=request.output,
            after_from=request.after_from
        )

        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(new_section_execution)
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
                    "error": f"An error occurred while adding the section execution: {str(e)}"}
        )


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
        
@router.put("/{section_execution_id}/modify_content")
async def modify_section_execution_content(section_execution_id: str,
                                           request: ModifySectionExecutionSchema,
                                           session: Session = Depends(get_session),
                                           transaction_id: str = Depends(get_transaction_id)):
    """
    Modify the content of a section execution.
    """
    try:
        section_execution_service = SectionExecutionService(session)
        await section_execution_service.update_section_execution_content(section_execution_id, request.new_content)
        
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"message": f"Content of section execution {section_execution_id} modified successfully."}
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
                    "error": f"An error occurred while modifying the content: {str(e)}"}
        )
