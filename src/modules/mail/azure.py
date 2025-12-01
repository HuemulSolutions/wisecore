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
        body_html = kwargs.get("body_html") or f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: 'Arial', sans-serif;
      background-color: #f9f9f9;
      margin: 0;
      padding: 0;
      color: #333;
    }}
    .container {{
      max-width: 600px;
      margin: 40px auto;
      padding: 20px;
      background-color: #fff;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }}
    .header {{
      text-align: center;
      border-bottom: 1px solid #eee;
      padding-bottom: 10px;
      margin-bottom: 20px;
    }}
    .header h2 {{
      margin: 0;
      font-size: 24px;
      color: #1C2544;
    }}
    .content {{
      text-align: center;
    }}
    .content p {{
      margin: 20px 0;
      line-height: 1.5;
    }}
    .code {{
      font-size: 1.8em;
      font-weight: bold;
      color: #1C2544;
      background-color: #f2f2f2;
      padding: 15px;
      border-radius: 8px;
      display: inline-block;
      margin: 20px 0;
    }}
    .footer {{
      text-align: center;
      margin-top: 30px;
      font-size: 0.9em;
      color: #777;
    }}
    .footer p {{
      margin: 5px 0;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Huemul Solutions</h2>
    </div>
    <div class="content">
      <p>Hola,</p>
      <p>Usa el siguiente código para validar tu cuenta:</p>
      <p class="code">{verification_code}</p>
    </div>
    <div class="footer">
      <p>¡Saludos!</p>
      <p>Equipo Huemul Solutions</p>
    </div>
  </div>
</body>
</html>"""

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
