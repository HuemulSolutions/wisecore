from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.organization_service import OrganizationService
from src.schemas import ResponseSchema
from src.utils import get_transaction_id


router = APIRouter(prefix="/organizations")


@router.get("/")
async def get_all_organizations(session: Session = Depends(get_session),
                                transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all organizations.
    """
    organization_service = OrganizationService(session)
    try:
        organizations = await organization_service.get_all_organizations()
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(organizations)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": f"An error occurred while retrieving organizations: {str(e)}"}
        )