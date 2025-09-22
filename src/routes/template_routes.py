from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.utils import get_transaction_id, get_organization_id
from src.services.template_service import TemplateService
from src.services.template_section_service import TemplateSectionService
from src.schemas import (ResponseSchema, CreateTemplate, CreateTemplateSection, 
                         CreateTemplateSectionDependency, UpdateSection, UpdateSectionOrder)

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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while creating the template: {str(e)}"}
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

        
@router.put("/sections/order")
async def update_template_section_order(update_order: UpdateSectionOrder,
                                        session: Session = Depends(get_session),
                                        transaction_id: str = Depends(get_transaction_id)):
    """
    Update the order of template sections.
    """
    template_section_service = TemplateSectionService(session)
    try:
        updated_order = await template_section_service.update_section_order(update_order.new_order)
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(updated_order)
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
                    "error": f"An error occurred while updating the section order: {str(e)}"}
        )
        


@router.post("/sections/")  
async def create_template_section(template_section: CreateTemplateSection,
                                  session: Session = Depends(get_session),
                                  transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new template section.
    """
    template_section_service = TemplateSectionService(session)
    try:
        created_section = await template_section_service.create_template_section(
            name=template_section.name,
            template_id=template_section.template_id,
            prompt=template_section.prompt,
            type=template_section.type,
            dependencies=template_section.dependencies or []
        )
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(created_section)
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
                    "error": f"An error occurred while creating the template section: {str(e)}"}
        )


@router.put("/sections/{section_id}")
async def update_template_section(section_id: str,
                                  template_section: UpdateSection,
                                  session: Session = Depends(get_session),
                                  transaction_id: str = Depends(get_transaction_id)):
    """ 
    Update an existing template section.
    """
    template_section_service = TemplateSectionService(session)
    try:
        updated_section = await template_section_service.update_template_section(
            id=section_id,
            name=template_section.name,
            prompt=template_section.prompt,
            dependencies=template_section.dependencies or []
        )
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(updated_section)
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
                    "error": f"An error occurred while updating the template section: {str(e)}"}
        )
        
@router.delete("/sections/{section_id}")
async def delete_template_section(section_id: str,
                                    session: Session = Depends(get_session),
                                    transaction_id: str = Depends(get_transaction_id)):
        """
        Delete a template section by its ID.
        """
        template_section_service = TemplateSectionService(session)
        try:
            await template_section_service.delete_template_section(section_id)
            response = ResponseSchema(
                transaction_id=transaction_id,
                data={"message": "Template section deleted successfully"}
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
                        "error": f"An error occurred while deleting the template section: {str(e)}"}
            )
        
@router.post("/sections/dependency/")
async def add_template_section_dependency(template_section_dependency: CreateTemplateSectionDependency,
                                          session: Session = Depends(get_session),
                                          transaction_id: str = Depends(get_transaction_id)):
    """
    Add a dependency relationship between two template sections.
    """
    template_section_service = TemplateSectionService(session)
    try:
        created_dependency = await template_section_service.add_dependency(template_section_dependency.section_id,
                                                                           template_section_dependency.depends_on_id)
        response = ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(created_dependency)
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
                    "error": f"An error occurred while adding the dependency: {str(e)}"}
        )
        
