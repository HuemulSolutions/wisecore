import logging
from typing import Optional

import requests
from requests import RequestException

from src.config import system_config
from .base import BaseMailProvider

logger = logging.getLogger(__name__)


class AzureMailProvider(BaseMailProvider):
    """
    Proveedor de correo basado en Microsoft Graph.
    Envía códigos de verificación utilizando las credenciales configuradas.
    """

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        sender: Optional[str] = None,
    ):
        self.tenant_id = tenant_id or system_config.EMAIL_AZURE_TENANT_ID
        self.client_id = client_id or system_config.EMAIL_AZURE_CLIENT_ID
        self.client_secret = client_secret or system_config.EMAIL_AZURE_CLIENT_SECRET
        self.sender = sender or system_config.EMAIL_AZURE_SENDER

        missing = [
            name
            for name, value in {
                "EMAIL_AZURE_TENANT_ID": self.tenant_id,
                "EMAIL_AZURE_CLIENT_ID": self.client_id,
                "EMAIL_AZURE_CLIENT_SECRET": self.client_secret,
                "EMAIL_AZURE_SENDER": self.sender,
            }.items()
            if not value
        ]

        if missing:
            raise ValueError(
                f"Faltan configuraciones para Azure Mail: {', '.join(missing)}"
            )

    def _get_azure_token(self) -> str:
        """Obtiene un token de acceso usando client_credentials."""
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }

        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise RuntimeError("Azure no devolvió un access_token")
        return token

    def send_verification_code(
        self, to_email: str, verification_code: str, **kwargs
    ) -> bool:
        """
        Envía un correo con el código de verificación al destinatario.

        Args:
            to_email: Destinatario del correo.
            verification_code: Código de verificación a enviar.
            **kwargs: Permite sobreescribir subject o body_html.
        """
        subject = kwargs.get("subject") or "Código de verificación"
        body_html = kwargs.get("body_html") or (
            "<p>Tu código de verificación es:</p>"
            f"<h2>{verification_code}</h2>"
            "<p>Introduce este código para continuar. "
            "Si no solicitaste este acceso, puedes ignorar este correo.</p>"
        )

        try:
            token = self._get_azure_token()
        except RequestException:
            logger.exception("Error al obtener el token de Azure AD")
            return False

        url = f"https://graph.microsoft.com/v1.0/users/{self.sender}/sendMail"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body_html,
                },
                "toRecipients": [
                    {
                        "emailAddress": {"address": to_email},
                    }
                ],
            },
            "saveToSentItems": False,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return True
        except RequestException:
            logger.exception("No se pudo enviar el correo de verificación a %s", to_email)
            return False
