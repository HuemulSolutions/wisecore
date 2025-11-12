from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from .base import SecretProvider
from src.config import system_config

class AzureKeyVaultProvider(SecretProvider):
    def __init__(self):
        vault_url = system_config.AZURE_KEY_VAULT_URL
        if not vault_url:
            raise ValueError("AZURE_KEY_VAULT_URL is required for AzureKeyVaultProvider")
        cred = DefaultAzureCredential()
        self._client = SecretClient(vault_url=vault_url, credential=cred)

    def get_secret(self, name: str) -> Optional[str]:
        try:
            return self._client.get_secret(name).value
        except Exception:
            return None  # o propaga según tu gusto

    def set_secret(self, value: str) -> str:
        try:
            name = self.generate_unique_name()
            self._client.set_secret(name, value)
            return name
        except Exception as e:
            raise Exception(f"Failed to set secret in Azure Key Vault: {str(e)}")
        