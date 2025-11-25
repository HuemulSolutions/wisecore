"""
Módulo de proveedores de correo electrónico.

Expone un factory similar al módulo `secrets` para obtener el proveedor
configurado mediante la variable EMAIL_PROVIDER.
"""

from functools import lru_cache

from src.config import system_config
from .base import BaseMailProvider
from .azure import AzureMailProvider


@lru_cache(maxsize=1)
def get_provider() -> BaseMailProvider:
    backend = (system_config.EMAIL_PROVIDER or "").lower()

    if backend == "azure":
        return AzureMailProvider()

    raise ValueError(f"EMAIL_PROVIDER '{backend}' no soportado")


def send_verification_code(
    to_email: str, verification_code: str, **kwargs
) -> bool:
    """Facade para enviar código sin exponer el proveedor a los servicios."""
    return get_provider().send_verification_code(
        to_email, verification_code, **kwargs
    )


__all__ = [
    "BaseMailProvider",
    "AzureMailProvider",
    "get_provider",
    "send_verification_code",
]
