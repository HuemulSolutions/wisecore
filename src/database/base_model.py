from sqlalchemy import Column, DateTime, UUID
from uuid import uuid4
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())