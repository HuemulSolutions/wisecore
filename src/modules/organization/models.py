from src.database.base_model import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class Organization(BaseModel):
    __tablename__ = "organization"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    documents = relationship("Document", back_populates="organization")
    templates = relationship("Template", back_populates="organization")
    folders = relationship("Folder", back_populates="organization")
    document_types = relationship("DocumentType", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"
