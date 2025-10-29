from src.database.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class SectionExecution(BaseModel):
    __tablename__ = "section_execution"

    name = Column(String, nullable=True) # Cambiar después de migración
    user_instruction = Column(String, nullable=True)
    prompt = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    output = Column(String, nullable=True)
    custom_output = Column(String, nullable=True)
    is_locked = Column(Boolean, default=False, nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id", ondelete="SET NULL"), nullable=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("execution.id"), nullable=False)
    
    
    section = relationship("Section", back_populates="section_executions")
    execution = relationship("Execution", back_populates="sections_executions")
    chunks = relationship("Chunk", back_populates="section_execution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SectionExecution(id={self.id}, user_instruction='{self.user_instruction}', output='{self.output}')>"
