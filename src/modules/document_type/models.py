from src.database.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class DocumentType(BaseModel):
    __tablename__ = "document_type"
    
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=True)
    organization = relationship("Organization", back_populates="document_types")
    
    documents = relationship("Document", back_populates="document_type")
    
    def __repr__(self):
        return f"<DocumentType(id={self.id}, name='{self.name}')>"