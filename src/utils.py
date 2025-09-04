from uuid import uuid4
from fastapi import Header, HTTPException
from typing import Optional

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