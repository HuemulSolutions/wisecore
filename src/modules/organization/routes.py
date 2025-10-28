from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.organization_service import OrganizationService
from src.schemas import ResponseSchema
from .schemas import CreateOrganization
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
        
@router.post("/")
async def create_organization(request: CreateOrganization,
                              session: Session = Depends(get_session),
                              transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new organization.
    """
    organization_service = OrganizationService(session)
    try:
        organization = await organization_service.create_organization(request.name, request.description)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(organization)
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
                    "error": f"An error occurred while creating the organization: {str(e)}"}
        )