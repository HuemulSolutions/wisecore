from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.library_services import LibraryService
from src.schemas import ResponseSchema, CreateNewFolder
from src.utils import get_transaction_id, get_organization_id

router = APIRouter(prefix="/library")


@router.post("/create_folder", response_model=ResponseSchema)
async def create_folder(request: CreateNewFolder, session: Session = Depends(get_session), 
                        transaction_id: str = Depends(get_transaction_id)):
    """
    Create a new folder. If parent_folder_id is provided, the new folder will be created as a subfolder.
    """ 
    try:
        service = LibraryService(session)
        new_folder = await service.create_folder(
            name=request.name, 
            organization_id=request.organization_id, 
            parent_folder_id=request.parent_folder_id
        )
        
        return ResponseSchema(
            data=jsonable_encoder(new_folder),
            transaction_id=transaction_id
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail={"transaction_id": transaction_id, "error": str(ve)})
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"transaction_id": transaction_id, 
                    "error": f"An error occurred while creating the folder: {str(e)}"}
        )

@router.get("/{folder_id}", response_model=ResponseSchema)
async def get_folder_content(folder_id: str, organization_id: str = Depends(get_organization_id), 
                             session: Session = Depends(get_session), transaction_id: str = Depends(get_transaction_id)):
    """
    Retrieve the contents of a folder by its ID.
    If folder_id is 'root', retrieve root-level folders and documents.
    """
    try:
        if folder_id == "root":
            folder_id = None  # Indicate root level

        service = LibraryService(session)
        content = await service.get_folder_content(folder_id, organization_id)
        
        return ResponseSchema(
            data=jsonable_encoder(content),
            message="Folder content retrieved successfully",
            transaction_id=transaction_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving folder content: {str(e)}")
    
    



