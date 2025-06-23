from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.utils import get_transaction_id
from src.services.template_service import TemplateService
from src.schemas import ResponseSchema, CreateTemplate

router = APIRouter(prefix="/templates")


@router.get("/{template_id}")
async def get_template(template_id: str,
                       session: Session = Depends(get_session),
                       transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve a template by its ID.
    """
    template_service = TemplateService(session)
    try:
        template = await template_service.get_template_by_id(template_id)
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(template)
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
                    "error": f"An error occurred while retrieving the template: {str(e)}"}
        )
        
@router.post("/")
async def create_template(template: CreateTemplate,
                          session: Session = Depends(get_session),
                          transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new template.
    """
    template_service = TemplateService(session)
    try:
        template = await template_service.create_template(template.name)
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(template)
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while creating the template: {str(e)}"}
        )