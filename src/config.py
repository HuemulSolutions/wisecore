import os
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass, fields
# Load environment variables from .env file
# load_dotenv()
load_dotenv(dotenv_path=Path(".env.dev"))
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

    def __post_init__(self):
        """Validate that all required environment variables are loaded correctly."""
        optional_vars = {
            "AZURE_KEY_VAULT_URL", "HASHICORP_VAULT_ADDR", "HASHICORP_VAULT_TOKEN"
        }
        
        for field in fields(self):
            value = getattr(self, field.name)
            # Solo validar variables requeridas (sin valor por defecto o con valor por defecto None)
            if field.name not in optional_vars and value is None:
                raise ValueError(f"Missing required environment variable: {field.name}")
            
system_config = Config()
