import os
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass, fields
# Load environment variables from .env file
load_dotenv(dotenv_path=Path(".env.local"))
# load_dotenv(dotenv_path=Path(".env.dev"))
# load_dotenv(dotenv_path=Path(".env.test"))
# load_dotenv(dotenv_path=Path(".env.prod"))


@dataclass
class Config:
    """
    Configuration class to hold application settings.
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "LOCAL")
    ALEMBIC_DATABASE_URL: str = os.getenv("ALEMBIC_DATABASE_URL", "")
    DEFAULT_LLM: str = os.getenv("DEFAULT_LLM", "gpt-4.1")
    MODEL_GATEWAY_URL: str = os.getenv("MODEL_GATEWAY_URL")
    MODEL_GATEWAY_APIKEY: str = os.getenv("MODEL_GATEWAY_APIKEY")
    JOB_WORKER_COUNT: int = int(os.getenv("JOB_WORKER_COUNT", "1"))
    SECRETS_PROVIDER: str = os.getenv("SECRETS_PROVIDER", "local")
    AZURE_KEY_VAULT_URL: str = os.getenv("AZURE_KEY_VAULT_URL")
    HASHICORP_VAULT_ADDR: str = os.getenv("HASHICORP_VAULT_ADDR")
    HASHICORP_VAULT_TOKEN: str = os.getenv("HASHICORP_VAULT_TOKEN")
    LOCAL_SECRETS_FILE: str = os.getenv("LOCAL_SECRETS_FILE", ".local_secrets.json")
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "azure")
    EMAIL_AZURE_TENANT_ID: str = os.getenv("EMAIL_AZURE_TENANT_ID")
    EMAIL_AZURE_CLIENT_ID: str = os.getenv("EMAIL_AZURE_CLIENT_ID")
    EMAIL_AZURE_CLIENT_SECRET: str = os.getenv("EMAIL_AZURE_CLIENT_SECRET")
    EMAIL_AZURE_SENDER: str = os.getenv("EMAIL_AZURE_SENDER")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    def __post_init__(self):
        """Validate that all required environment variables are loaded correctly."""
        optional_vars = {
            "AZURE_KEY_VAULT_URL", "HASHICORP_VAULT_ADDR", "HASHICORP_VAULT_TOKEN",
            "MODEL_GATEWAY_URL", "MODEL_GATEWAY_APIKEY", "LOCAL_SECRETS_FILE",
            "JWT_ALGORITHM", "JWT_EXPIRE_MINUTES", "EMAIL_AZURE_TENANT_ID",
            "EMAIL_AZURE_CLIENT_ID", "EMAIL_AZURE_CLIENT_SECRET", "EMAIL_AZURE_SENDER",
            "JWT_SECRET_KEY"
        }
        
        for field in fields(self):
            value = getattr(self, field.name)
            # Solo validar variables requeridas (sin valor por defecto o con valor por defecto None)
            if field.name not in optional_vars and value is None:
                raise ValueError(f"Missing required environment variable: {field.name}")
            
system_config = Config()
