from enum import Enum
from sqlalchemy import Column, String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from src.database.base_model import BaseModel

class AuthTypeEnum(str, Enum):
    """Supported authentication types."""

    INTERNAL = "internal"
    ENTRA = "entra"
    
    
class AuthType(BaseModel):
    __tablename__ = "auth_types"
    
    name = Column(String(50), unique=True, nullable=False)
    type = Column(SAEnum(AuthTypeEnum), nullable=False)
    params = Column(JSONB, nullable=True)