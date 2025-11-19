from typing import Optional
import hvac
from .base import SecretProvider
from src.config import system_config

class HashiCorpVaultProvider(SecretProvider):
    def __init__(self):
        vault_addr = system_config.HASHICORP_VAULT_ADDR
        vault_token = system_config.HASHICORP_VAULT_TOKEN
        
        if not vault_addr:
            raise ValueError("HASHICORP_VAULT_ADDR is required for HashiCorpVaultProvider")
        if not vault_token:
            raise ValueError("HASHICORP_VAULT_TOKEN is required for HashiCorpVaultProvider")
            
        self._client = hvac.Client(url=vault_addr, token=vault_token)
        
        # Verificar que el cliente esté autenticado
        if not self._client.is_authenticated():
            raise ValueError("Failed to authenticate with HashiCorp Vault")

    def get_secret(self, name: str, mount_point: str = "secret") -> Optional[str]:
        try:
            response = self._client.secrets.kv.v2.read_secret_version(
                path=name, 
                mount_point=mount_point
            )
            return response['data']['data'].get('value')
        except Exception:
            return None

    def set_secret(self, value: str, mount_point: str = "secret") -> str:
        try:
            name = self.generate_unique_name()
            self._client.secrets.kv.v2.create_or_update_secret(
                path=name,
                secret={'value': value},
                mount_point=mount_point
            )
            return name
        except Exception as e:
            raise Exception(f"Failed to set secret in HashiCorp Vault: {str(e)}")
