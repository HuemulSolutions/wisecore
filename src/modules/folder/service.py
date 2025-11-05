from sqlalchemy.ext.asyncio import AsyncSession
from .repository import FolderRepo

class FolderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.folder_repo = FolderRepo(session)
        
    async def get_folder_content(self, folder_id: str = None, organization_id: str = None):
        """
        Retrieve the contents of a folder by its ID.
        If folder_id is None, retrieve root-level folders and documents.
        Returns a dictionary with folder name and its contents (folders and documents in one list).
        """
        return await self.folder_repo.get_folder_content(folder_id, organization_id)
    
    async def create_folder(self, name: str, organization_id: str = None, parent_folder_id: str = None):
        """
        Create a new folder. If parent_folder_id is provided, the new folder will be created as a subfolder.
        """
        existing_folder = await self.folder_repo.get_by_name(name, parent_folder_id)
        if existing_folder:
            raise ValueError(f"Folder with name '{name}' already exists in the specified location.")
        
        if organization_id is None:
            parent_folder = await self.folder_repo.get_by_id(parent_folder_id)
            if parent_folder is None:
                raise ValueError(f"Parent folder with ID '{parent_folder_id}' not found.")
            organization_id = parent_folder.organization_id
        new_folder = self.folder_repo.model(
            name=name,
            organization_id=organization_id,
            parent_folder_id=parent_folder_id
        )
        await self.folder_repo.add(new_folder)
        return new_folder
    
    async def delete_folder(self, folder_id: str):
        """
        Delete a folder by its ID. This will also delete all subfolders and documents within it.
        """
        folder = await self.folder_repo.get_by_id(folder_id)
        if not folder:
            raise ValueError(f"Folder with ID '{folder_id}' not found.")
        
        await self.folder_repo.delete(folder)
        return True
        