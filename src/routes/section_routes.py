from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.utils import get_transaction_id
from src.database.repositories.section_repo import SectionRepo
from src.database.models import Section
from src.schemas import ResponseSchema, CreateDocumentSection, UpdateSection
from src.services.document_section_service import SectionService


router = APIRouter(prefix="/sections")

@router.post("/")
async def create_document_section(section: CreateDocumentSection,
                                  session: Session = Depends(get_session),
                                  transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new section in a document.
    """
    section_service = SectionService(session)
    try:
        new_section = await section_service.create_section(
            document_id=section.document_id,
            name=section.name,
            type=section.type,
            prompt=section.prompt,
            dependencies=section.dependencies or []
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(new_section)
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
                    "error": f"An error occurred while creating the section: {str(e)}"}
        )
        
@router.put("/{section_id}")
async def update_document_section(section_id: str,
                                  section: UpdateSection,
                                  session: Session = Depends(get_session),
                                  transaction_id: str = Depends(get_transaction_id)):
    """ 
    Update an existing section in a document.
    """
    section_service = SectionService(session)
    try:
        updated_section = await section_service.update_section(
            section_id=section_id,
            name=section.name,
            prompt=section.prompt,
            dependencies=section.dependencies or []
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(updated_section)
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
                    "error": f"An error occurred while updating the section: {str(e)}"}
        )
                                  
        