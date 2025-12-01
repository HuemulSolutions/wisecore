from sqlalchemy import Column, String, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.base_model import BaseModel
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"    


class Execution(BaseModel):
    __tablename__ = "execution"
    
    name = Column(String, nullable=False)
    user_instruction = Column(String, nullable=True)
    status = Column(SAEnum(Status, name="status_enum"), nullable=False)
    status_message = Column(String, nullable=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("llm.id"), nullable=True)
    
    document = relationship("Document", back_populates="executions")
    model = relationship("LLM", back_populates="executions")
    sections_executions = relationship("SectionExecution", back_populates="execution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Execution(id={self.id}, status={self.status.value}, document_id={self.document.name})>"