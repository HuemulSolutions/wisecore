import json
from pathlib import Path
from threading import Lock
from typing import Optional

from .base import SecretProvider
from src.config import system_config


class LocalFileSecretProvider(SecretProvider):
    """
    Stores secrets in a local JSON file for development.
    NOT for production use.
    """

    def __init__(self, file_path: Optional[str] = None):
        path_value = file_path or system_config.LOCAL_SECRETS_FILE or ".local_secrets.json"
        self._path = Path(path_value).expanduser()
        if not self._path.is_absolute():
            # Anchor relative paths to the project root
            project_root = Path(__file__).resolve().parents[3]
            self._path = (project_root / self._path).resolve()

        self._lock = Lock()
        self._ensure_storage()

    def get_secret(self, name: str) -> Optional[str]:
        with self._lock:
            data = self._load_all()
            return data.get(name)

    def set_secret(self, value: str) -> str:
        with self._lock:
            data = self._load_all()
            name = self.generate_unique_name()
            data[name] = value
            self._write_all(data)
            return name

    def _ensure_storage(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("{}", encoding="utf-8")

    def _load_all(self) -> dict:
        if not self._path.exists():
            return {}
        raw = self._path.read_text(encoding="utf-8").strip()
        if not raw:
            return {}
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return {}

    def _write_all(self, data: dict) -> None:
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")
