from src.database.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class LLM(BaseModel):
    __tablename__ = "llm"
    
    name = Column(String, nullable=False)
    internal_name = Column(String, nullable=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("provider.id"), nullable=True)
    is_default = Column(Boolean, default=False)
    executions = relationship("Execution", back_populates="model")
    provider = relationship("Provider", back_populates="llms")
    
    def __repr__(self):
        return f"<LLM(id={self.id}, name='{self.name}')>"