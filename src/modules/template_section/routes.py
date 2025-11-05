from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from src.database.core import get_session
from src.utils import get_transaction_id
from src.schemas import ResponseSchema
from .schemas import (CreateTemplateSection, UpdateTemplateSection, 
                      CreateTemplateSectionDependency, UpdateSectionOrder)
from .service import TemplateSectionService

router = APIRouter(prefix="/template_section")

@router.post("/dependency/")
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
        
@router.put("/order")
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

@router.post("/")  
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
        
@router.put("/{section_id}")
async def update_template_section(section_id: str,
                                  template_section: UpdateTemplateSection,
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
        
@router.delete("/{section_id}")
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
        
