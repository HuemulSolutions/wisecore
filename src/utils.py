from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional, Tuple, Dict, Any
from fastapi import Request
import jwt
from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config import system_config

def get_transaction_id() -> str:
    return str(uuid4())

def get_organization_id(organization_id: Optional[str] = Header(None, alias="OrganizationId")) -> str:
    """
    Extrae el OrganizationId del header de la request.
    
    Args:
        organization_id: El valor del header OrganizationId
        
    Returns:
        str: El OrganizationId extraído del header
        
    Raises:
        HTTPException: Si el header OrganizationId no está presente
    """
    if organization_id is None:
        raise HTTPException(
            status_code=400,
            detail="Header OrganizationId es requerido"
        )
    return organization_id

def get_current_user(request: Request):
    payload = getattr(request.state, "jwt_payload", None)
    if payload is None:
        # Si llegas aquí en teoría es error de config
        raise HTTPException(status_code=401, detail="Not authenticated")
    return payload  # o cargar el User desde la DB


def generate_jwt_token(payload: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un token JWT firmado con la configuración actual.
    
    Args:
        payload: Datos que se quieren incluir en el token.
        expires_delta: Tiempo de expiración opcional. Si no se provee, usa JWT_EXPIRE_MINUTES.
    
    Returns:
        str: Token JWT firmado.
    """
    token_payload = payload.copy()
    expiration = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=system_config.JWT_EXPIRE_MINUTES)
    )
    token_payload["exp"] = expiration

    return jwt.encode(
        token_payload,
        system_config.JWT_SECRET_KEY,
        algorithm=system_config.JWT_ALGORITHM,
    )
