from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from src.database.base_model import BaseModel
  
class Provider(BaseModel):
    __tablename__ = "provider"
    
    name = Column(String, nullable=False)
    key = Column(String, nullable=True)
    endpoint = Column(String, nullable=True)
    deployment = Column(String, nullable=True)
    
    llms = relationship("LLM", back_populates="provider")