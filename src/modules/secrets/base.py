from abc import ABC, abstractmethod
from typing import Optional
import uuid

class SecretProvider(ABC):
    @abstractmethod
    def get_secret(self, name: str) -> Optional[str]:
        ...

    @abstractmethod
    def set_secret(self, value: str) -> str:
        ...

    def generate_unique_name(self, prefix: str = "secret") -> str:
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}-{unique_id}"
