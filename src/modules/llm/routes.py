from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from .service import LLMService
from src.schemas import ResponseSchema
from src.utils import get_transaction_id


router = APIRouter(prefix="/llms")

@router.get("/")
async def get_all_llms(session: Session = Depends(get_session),
                       transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all LLMs.
    """
    try:
        # Assuming LLMService is implemented similarly to other services
        llm_service = LLMService(session)
        llms = await llm_service.get_all_llms()
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(llms)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id, 
                    "error": f"An error occurred while retrieving LLMs: {str(e)}"}
        )