"""JSON persistence layer (kept separate so it can be swapped for a DB later)."""
import json
import logging
import os
import tempfile

from exceptions import StorageError

log = logging.getLogger(__name__)


class JsonStorage:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> dict:
        if not os.path.exists(self.path):
            return {"books": [], "members": []}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            log.error("Failed to load %s: %s", self.path, exc)
            raise StorageError(f"Could not read data file '{self.path}': {exc}") from exc

    def save(self, data: dict) -> None:
        """Atomic write: write to a temp file, then replace, so a crash can't corrupt data."""
        folder = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(folder, exist_ok=True)
        try:
            fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, self.path)
        except OSError as exc:
            log.error("Failed to save %s: %s", self.path, exc)
            raise StorageError(f"Could not write data file '{self.path}': {exc}") from exc
