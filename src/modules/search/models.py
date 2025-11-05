from src.database.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

class Chunk(BaseModel):
    __tablename__ = "chunk"

    content = Column(String, nullable=False)
    embedding = Column(Vector(3072), nullable=False)
    section_execution_id = Column(UUID(as_uuid=True), ForeignKey("section_execution.id"), nullable=False)
    
    section_execution = relationship("SectionExecution", back_populates="chunks")