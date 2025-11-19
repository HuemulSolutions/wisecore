from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session

from src.database.core import get_session
from src.schemas import ResponseSchema
from src.utils import get_transaction_id
from .schemas import CreateProvider, UpdateProvider
from .service import LLMProviderService

router = APIRouter(prefix="/llm_provider")


@router.get("/supported")
async def get_supported_providers(
    transaction_id: str = Depends(get_transaction_id),
    session: Session = Depends(get_session),
):
    """Return the providers supported by the platform."""
    provider_service = LLMProviderService(session)
    return ResponseSchema(
        transaction_id=transaction_id,
        data=provider_service.get_supported_providers(),
    )


@router.get("/")
async def list_providers(
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Retrieve every registered LLM provider.
    """
    provider_service = LLMProviderService(session)
    try:
        providers = await provider_service.get_all_providers()
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(providers),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while listing providers: {str(exc)}",
            },
        )


@router.get("/{provider_id}")
async def get_provider(
    provider_id: str,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Retrieve a provider by its identifier.
    """
    provider_service = LLMProviderService(session)
    try:
        provider = await provider_service.get_provider_by_id(provider_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(provider),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while retrieving the provider: {str(exc)}",
            },
        )


@router.post("/")
async def create_provider(
    request: CreateProvider,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Create a new LLM provider.
    """
    provider_service = LLMProviderService(session)
    try:
        provider = await provider_service.create_provider(
            name=request.name,
            key=request.key,
            endpoint=request.endpoint,
            deployment=request.deployment,
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(provider),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while creating the provider: {str(exc)}",
            },
        )


@router.put("/{provider_id}")
async def update_provider(
    provider_id: str,
    request: UpdateProvider,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Update an existing LLM provider.
    """
    provider_service = LLMProviderService(session)

    update_data = request.model_dump(exclude_unset=True)

    try:
        provider = await provider_service.update_provider(
            provider_id=provider_id,
            name=update_data.get("name"),
            key=update_data.get("key"),
            endpoint=update_data.get("endpoint"),
            deployment=update_data.get("deployment"),
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(provider),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while updating the provider: {str(exc)}",
            },
        )


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: str,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Delete an LLM provider.
    """
    provider_service = LLMProviderService(session)
    try:
        await provider_service.delete_provider(provider_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"message": "Provider deleted successfully"},
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"An error occurred while deleting the provider: {str(exc)}",
            },
        )
