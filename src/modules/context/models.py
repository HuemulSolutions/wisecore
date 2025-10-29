from src.database.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class Context(BaseModel):
    __tablename__ = "context"
    
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    document = relationship("Document", back_populates="contexts")
    
    def __repr__(self):
        return f"<Context(id={self.id}, name='{self.name}', document_id={self.document_id})>"