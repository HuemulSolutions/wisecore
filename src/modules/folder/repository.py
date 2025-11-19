from uuid import UUID
from typing import Dict, Any, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.base_repo import BaseRepository
from src.modules.document.models import Document

from .models import Folder

class FolderRepo(BaseRepository[Folder]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Folder)
        
        
    async def get_by_name(
        self,
        name: str,
        organization_id: Union[str, UUID],
        parent_folder_id: Optional[str] = None,
        exclude_id: Optional[str] = None,
    ) -> Folder:
        """
        Retrieve a folder by its name, organization, and optional parent.
        Allows excluding a specific folder ID (useful when renaming).
        """
        query = (
            select(self.model)
            .where(self.model.name == name)
            .where(self.model.organization_id == organization_id)
        )
        if parent_folder_id is None:
            query = query.where(self.model.parent_folder_id.is_(None))
        else:
            query = query.where(self.model.parent_folder_id == parent_folder_id)

        if exclude_id:
            query = query.where(self.model.id != exclude_id)

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
            documents_query = select(Document).options(selectinload(Document.document_type)).where(Document.folder_id == folder_id)
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
            root_documents_query = select(Document).options(selectinload(Document.document_type)).where(Document.folder_id.is_(None))
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
                "type": "document",
                "document_type": {
                    "id": str(document.document_type.id),
                    "name": document.document_type.name,
                    "color": document.document_type.color
                }
            })
        
        return result
        
