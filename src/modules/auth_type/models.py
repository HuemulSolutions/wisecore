from enum import Enum

from sqlalchemy import Column, String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.database.base_model import BaseModel


class AuthTypeEnum(str, Enum):
    """Supported authentication types."""
    
    INTERNAL = "internal"
    ENTRA = "entra"


class AuthType(BaseModel):
    __tablename__ = "auth_types"

    name = Column(String(100), nullable=False, unique=True)
    type = Column(SAEnum(AuthTypeEnum), nullable=False)
    params = Column(JSONB, nullable=True)
    
    users = relationship("User", back_populates="auth_type")
