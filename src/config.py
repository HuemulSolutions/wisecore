import os
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass, fields

BASE_DIR = Path(__file__).resolve().parents[1]

# Always load the shared .env file first (if present) to provide defaults.
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)

ENVIRONMENT = os.getenv("ENVIRONMENT", "LOCAL").upper()
ENV_FILE_MAP = {
    "LOCAL": ".env.local",
    "DEV": ".env.dev",
    "TEST": ".env.test",
    "PROD": ".env.prod",
}

env_file = ENV_FILE_MAP.get(ENVIRONMENT, ".env.local")
env_path = BASE_DIR / env_file
if env_path.exists():
    # Specific env files override the shared defaults.
    load_dotenv(dotenv_path=env_path, override=True)


@dataclass
class Config:
    """
    Configuration class to hold application settings.
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ENVIRONMENT: str = ENVIRONMENT
    ALEMBIC_DATABASE_URL: str = os.getenv("ALEMBIC_DATABASE_URL", "")
    DEFAULT_LLM: str = os.getenv("DEFAULT_LLM", "gpt-4.1")
    MODEL_GATEWAY_URL: str = os.getenv("MODEL_GATEWAY_URL")
    MODEL_GATEWAY_APIKEY: str = os.getenv("MODEL_GATEWAY_APIKEY")
    JOB_WORKER_COUNT: int = int(os.getenv("JOB_WORKER_COUNT", "1"))
    SECRETS_PROVIDER: str = os.getenv("SECRETS_PROVIDER", "local")
    AZURE_KEY_VAULT_URL: str = os.getenv("AZURE_KEY_VAULT_URL")
    HASHICORP_VAULT_ADDR: str = os.getenv("HASHICORP_VAULT_ADDR")
    HASHICORP_VAULT_TOKEN: str = os.getenv("HASHICORP_VAULT_TOKEN")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL")
    TEST_ALEMBIC_DATABASE_URL: str = os.getenv("TEST_ALEMBIC_DATABASE_URL")

    def __post_init__(self):
        """Validate that all required environment variables are loaded correctly."""
        optional_vars = {
            "AZURE_KEY_VAULT_URL", "HASHICORP_VAULT_ADDR", "HASHICORP_VAULT_TOKEN",
            "MODEL_GATEWAY_URL", "MODEL_GATEWAY_APIKEY",
            "TEST_DATABASE_URL", "TEST_ALEMBIC_DATABASE_URL"
        }

        self.ENVIRONMENT = (self.ENVIRONMENT or "LOCAL").upper()

        for field in fields(self):
            value = getattr(self, field.name)
            # Solo validar variables requeridas (sin valor por defecto o con valor por defecto None)
            if field.name not in optional_vars and value is None:
                raise ValueError(f"Missing required environment variable: {field.name}")

        if self.ENVIRONMENT == "TEST":
            if self.TEST_DATABASE_URL:
                self.DATABASE_URL = self.TEST_DATABASE_URL
            if self.TEST_ALEMBIC_DATABASE_URL:
                self.ALEMBIC_DATABASE_URL = self.TEST_ALEMBIC_DATABASE_URL
            elif not self.ALEMBIC_DATABASE_URL and self.DATABASE_URL:
                # Derive a sync-friendly URL for Alembic if only the async URL is provided.
                self.ALEMBIC_DATABASE_URL = self.DATABASE_URL.replace("+asyncpg", "")

system_config = Config()
