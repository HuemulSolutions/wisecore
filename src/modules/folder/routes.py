from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.library_services import LibraryService
from src.schemas import ResponseSchema
from .schemas import CreateNewFolder
from src.utils import get_transaction_id, get_organization_id

router = APIRouter(prefix="/folder")


@router.post("/create_folder", response_model=ResponseSchema)
async def create_folder(request: CreateNewFolder, 
                        session: Session = Depends(get_session), 
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
    

@router.delete("/{folder_id}", response_model=ResponseSchema)
async def delete_folder(folder_id: str, session: Session = Depends(get_session), 
                        transaction_id: str = Depends(get_transaction_id)):
    """
    Delete a folder by its ID. This will also delete all subfolders and documents within it.
    """
    try:
        service = LibraryService(session)
        await service.delete_folder(folder_id)
        
        return ResponseSchema(
            data={"folder_id": folder_id},
            message="Folder deleted successfully",
            transaction_id=transaction_id
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail={"transaction_id": transaction_id, "error": str(ve)})
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"transaction_id": transaction_id, 
                    "error": f"An error occurred while deleting the folder: {str(e)}"}
        )


