from src.database.base_model import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class LLM(BaseModel):
    __tablename__ = "llm"
    
    name = Column(String, nullable=False)
    executions = relationship("Execution", back_populates="model")
    
    def __repr__(self):
        return f"<LLM(id={self.id}, name='{self.name}')>"