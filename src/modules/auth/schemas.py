from typing import Optional

from pydantic import BaseModel, EmailStr, model_validator

from .models import CodePurpose


class CreateUser(BaseModel):
    """Payload para crear un usuario."""

    username: str
    email: EmailStr
    code: str


class RequestCode(BaseModel):
    """Payload para solicitar un código de acceso (registro o login)."""

    email: EmailStr
    purpose: CodePurpose


class VerifyCode(BaseModel):
    """Payload para verificar un código de acceso."""

    email: EmailStr
    code: str
