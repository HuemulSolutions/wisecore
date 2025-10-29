from src.database.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class Folder(BaseModel):
    __tablename__ = "folder"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    parent_folder_id = Column(UUID(as_uuid=True), ForeignKey("folder.id"), nullable=True)
    
    # Relaciones
    organization = relationship("Organization", back_populates="folders")
    parent_folder = relationship("Folder", remote_side="Folder.id", back_populates="subfolders")
    subfolders = relationship("Folder", back_populates="parent_folder", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="folder", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Folder(id={self.id}, name='{self.name}', parent_id={self.parent_folder_id})>"
    
    @property
    def full_path(self):
        """Retorna la ruta completa de la carpeta"""
        if self.parent_folder:
            return f"{self.parent_folder.full_path}/{self.name}"
        return self.name
    
    @property
    def is_root(self):
        """Indica si es una carpeta raíz (sin padre)"""
        return self.parent_folder_id is None