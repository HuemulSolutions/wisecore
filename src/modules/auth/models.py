from datetime import datetime, timedelta, timezone
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.database.base_model import BaseModel


class CodePurpose(str, Enum):
    """Supported verification code purposes."""

    SIGNUP = "signup"
    LOGIN = "login"
    
class UserStatus(str, Enum):
    """Supported user statuses."""

    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True, default="")
    last_name = Column(String(100), nullable=True, default="")
    birthdate = Column(DateTime, nullable=True)
    is_root_admin = Column(Boolean, default=False)
    status = Column(String(50), default=UserStatus.PENDING, nullable=False)
    activated_at = Column(DateTime, nullable=True)
    photo_url = Column(String(255), nullable=True)
    external_id = Column(String(100), nullable=True) # ID from external auth providers, no se usa por ahora
    user_metadata = Column(JSONB, nullable=True) # Información adicional del usuario, no se usa por ahora
    auth_type_id = Column(UUID(as_uuid=True), ForeignKey("auth_types.id"), nullable=False)

    login_codes = relationship(
        "LoginCode", back_populates="user", cascade="all, delete-orphan"
    )
    auth_type = relationship("AuthType")


class LoginCode(BaseModel):
    __tablename__ = "login_codes"

    # user_id can be null for sign-up codes (user not created yet)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    email = Column(String(100), nullable=False, index=True)
    purpose = Column(String(20), nullable=False, default=CodePurpose.LOGIN.value)
    code = Column(String(6), nullable=False)
    expires_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
        + timedelta(minutes=15),
    )
    is_used = Column(Boolean, default=False, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="login_codes")

    def is_expired(self) -> bool:
        """Verifica si el código ha expirado."""
        expires_at = (
            self.expires_at.astimezone(timezone.utc)
            if self.expires_at.tzinfo and self.expires_at.tzinfo.utcoffset(self.expires_at) is not None
            else self.expires_at
        )
        now = (
            datetime.now(timezone.utc)
            if expires_at.tzinfo
            else datetime.now(timezone.utc).replace(tzinfo=None)
        )
        return now > expires_at

    def is_valid(self) -> bool:
        """Verifica si el código es válido (no usado y no expirado)."""
        return not self.is_used and not self.is_expired() and self.attempts < 3
