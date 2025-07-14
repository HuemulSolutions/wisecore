from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.utils import get_transaction_id
from src.services.template_service import TemplateService
from src.services.template_section_service import TemplateSectionService
from src.schemas import ResponseSchema, CreateTemplate, CreateTemplateSection, CreateTemplateSectionDependency

router = APIRouter(prefix="/templates")


@router.get("/")
async def get_all_templates(session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve all templates.
    """
    template_service = TemplateService(session)
    try:
        templates = await template_service.get_all_templates()
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
                          session: Session = Depends(get_session),
                          transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new template.
    """
    template_service = TemplateService(session)
    try:
        template = await template_service.create_template(template.name, 
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