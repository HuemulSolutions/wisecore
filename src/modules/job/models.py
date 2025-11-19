from src.database.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    __tablename__ = "job"
    
    type = Column(String, nullable=False)
    payload = Column(String, nullable=True)
    status = Column(String, nullable=False, default=JobStatus.PENDING.value)
    result = Column(String, nullable=True)