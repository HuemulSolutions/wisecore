import os
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass, fields
# Load environment variables from .env file
# load_dotenv()
load_dotenv(dotenv_path=Path(".env.dev"))

@dataclass
class Config:
    """
    Configuration class to hold application settings.
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    WATSONX_APIKEY: str = os.getenv("WATSONX_APIKEY")
    WATSONX_URL: str = os.getenv("WATSONX_URL")
    WATSONX_PROJECT_ID: str = os.getenv("WATSONX_PROJECT_ID")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "LOCAL")
    ALEMBIC_DATABASE_URL: str = os.getenv("ALEMBIC_DATABASE_URL", "")
    DEFAULT_LLM: str = os.getenv("DEFAULT_LLM", "gpt-4.1")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")

    def __post_init__(self):
        """Validate that all environment variables are loaded correctly."""
        for field in fields(self):
            if getattr(self, field.name) is None:
                raise ValueError(f"Missing required environment variable: {field.name}")
            
system_config = Config()