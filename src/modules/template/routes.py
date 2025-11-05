from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.utils import get_transaction_id, get_organization_id
from src.schemas import (ResponseSchema)
from .schemas import (CreateTemplate, UpdateTemplate)
from .service import TemplateService

router = APIRouter(prefix="/templates")


@router.get("/")
async def get_all_templates(organization_id: str = Depends(get_organization_id),
                            session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all templates.
    """
    print("Organization ID:", organization_id)  # Debugging line
    template_service = TemplateService(session)
    try:
        templates = await template_service.get_all_templates(organization_id)
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(templates)
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while retrieving templates: {str(e)}"}
        )


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
                          organization_id: str = Depends(get_organization_id),
                          session: Session = Depends(get_session),
                          transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new template.
    """
    template_service = TemplateService(session)
    try:
        template = await template_service.create_template(name=template.name,
                                                          organization_id=organization_id, 
                                                          description=template.description)
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(template)
        )
        return response
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
                    "error": f"An error occurred while creating the template: {str(e)}"}
        )

@router.put("/{template_id}")
async def update_template(template_id: str,
                          template: UpdateTemplate,
                          session: Session = Depends(get_session),
                          transaction_id: str = Depends(get_transaction_id)):
    """
    Update a template's name and/or description.
    """
    template_service = TemplateService(session)
    try:
        updated_template = await template_service.update_template(
            template_id=template_id,
            name=template.name,
            description=template.description
        )
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(updated_template)
        )
        return response
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
                    "error": f"An error occurred while updating the template: {str(e)}"}
        )


@router.delete("/{template_id}")
async def delete_template(template_id: str,
                            session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
        """
        Delete a template by its ID.
        """
        template_service = TemplateService(session)
        try:
            await template_service.delete_template(template_id)
            response = ResponseSchema(
                transaction_id=transaction_id,
                data={"message": "Template deleted successfully"}
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
                        "error": f"An error occurred while deleting the template: {str(e)}"}
            )


@router.get("/{template_id}/export")
async def export_template(template_id: str,
                         session: Session = Depends(get_session),
                         transaction_id: str = Depends(get_transaction_id)):
    """
    Export a template to JSON format for download.
    Returns a JSON file with template specifications excluding internal IDs and metadata.
    """
    template_service = TemplateService(session)
    try:
        export_data = await template_service.export_template(template_id)
        
        # Return as JSON response with appropriate headers for file download
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f"attachment; filename={export_data['name']}_template.json",
                "Content-Type": "application/json"
            }
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
                    "error": f"An error occurred while exporting the template: {str(e)}"}
        )

@router.post("/{template_id}/generate")
async def generate_template_structure(template_id: str,
                                      session: Session = Depends(get_session),
                                      transaction_id: str = Depends(get_transaction_id)):
    """
    Generate the structure of a template using AI.
    """
    template_service = TemplateService(session)
    try:
        generated_template = await template_service.generate_template_structure(template_id)
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(generated_template)
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
                    "error": f"An error occurred while generating the template structure: {str(e)}"}
        )
