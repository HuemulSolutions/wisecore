from .base_repo import BaseRepository
from ..models import Folder, Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import Dict, List, Any, Optional

class FolderRepo(BaseRepository[Folder]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Folder)
        
        
    async def get_by_name(self, name: str, parent_folder_id: Optional[str] = None) -> Folder:
        """
        Retrieve a folder by its name and optional parent_folder_id.
        """
        query = select(self.model).where(self.model.name == name and self.model.parent_folder_id == parent_folder_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        
        
    async def get_folder_content(self, folder_id: str = None, organization_id: str = None) -> Dict[str, Any]:
        """
        Retrieve the contents of a folder by its ID.
        If folder_id is None, retrieve root-level folders and documents.
        Returns a dictionary with folder name and its contents (folders and documents in one list).
        """
        result = {
            "folder_name": "root",
            "parent_id": None,
            "content": []
        }
        
        if folder_id:
            # Get the specific folder
            folder = await self.get_by_id(folder_id)
            if not folder:
                return result
            
            result["folder_name"] = folder.name
            result["parent_id"] = str(folder.parent_folder_id) if folder.parent_folder_id else None
            
            # Get subfolders
            subfolders_query = select(Folder).where(Folder.parent_folder_id == folder_id)
            subfolders_result = await self.session.execute(subfolders_query)
            subfolders = subfolders_result.scalars().all()
            
            # Get documents in this folder
            documents_query = select(Document).where(Document.folder_id == folder_id)
            documents_result = await self.session.execute(documents_query)
            documents = documents_result.scalars().all()
            
        else:
            # Get root-level folders (no parent)
            root_folders_query = select(Folder).where(Folder.parent_folder_id.is_(None))
            if organization_id:
                root_folders_query = root_folders_query.where(Folder.organization_id == organization_id)
            
            root_folders_result = await self.session.execute(root_folders_query)
            subfolders = root_folders_result.scalars().all()
            
            # Get root-level documents (no folder)
            root_documents_query = select(Document).where(Document.folder_id.is_(None))
            if organization_id:
                root_documents_query = root_documents_query.where(Document.organization_id == organization_id)
                
            root_documents_result = await self.session.execute(root_documents_query)
            documents = root_documents_result.scalars().all()
        
        # Add folders first
        for subfolder in subfolders:
            result["content"].append({
                "id": str(subfolder.id),
                "name": subfolder.name,
                "type": "folder"
            })
        
        # Add documents after folders
        for document in documents:
            result["content"].append({
                "id": str(document.id),
                "name": document.name,
                "type": "document"
            })
        
        return result
        