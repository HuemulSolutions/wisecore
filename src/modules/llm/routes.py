from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from .service import LLMService
from src.schemas import ResponseSchema
from src.utils import get_transaction_id
from .schemas import CreateLLM, SetDefaultLLM, UpdateLLM


router = APIRouter(prefix="/llms")


@router.get("/")
async def get_all_llms(
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Retrieve all LLMs.
    """
    try:
        llm_service = LLMService(session)
        llms = await llm_service.get_all_llms()
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(llms),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while retrieving LLMs: {str(e)}",
            },
        )


@router.post("/")
async def create_llm(
    request: CreateLLM,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Create a new LLM associated with a provider.
    """
    llm_service = LLMService(session)
    try:
        llm = await llm_service.create_llm(
            name=request.name,
            internal_name=request.internal_name,
            provider_id=request.provider_id,
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(llm),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while creating the LLM: {str(e)}",
            },
        )


@router.put("/{llm_id}")
async def update_llm(
    llm_id: str,
    request: UpdateLLM,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Update fields of an existing LLM.
    """
    llm_service = LLMService(session)
    update_data = request.model_dump(exclude_unset=True)
    try:
        llm = await llm_service.update_llm(
            llm_id=llm_id,
            name=update_data.get("name"),
            internal_name=update_data.get("internal_name"),
            provider_id=update_data.get("provider_id"),
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(llm),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while updating the LLM: {str(e)}",
            },
        )


@router.patch("/set-default")
async def set_default_llm(
    request: SetDefaultLLM,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Set an LLM as the default one.
    """
    llm_service = LLMService(session)
    try:
        llm = await llm_service.set_default_llm(request.llm_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(llm),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while setting default LLM: {str(e)}",
            },
        )


@router.get("/default")
async def get_default_llm(
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Retrieve the default LLM.
    """
    try:
        llm_service = LLMService(session)
        llm = await llm_service.get_default_llm()
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(llm),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail={"transaction_id": transaction_id, "error": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while retrieving default LLM: {str(e)}",
            },
        )
