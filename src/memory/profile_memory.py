"""Long-term profile: Redis nếu có REDIS_URL, không thì JSON file (KV)."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from src.config import DATA_DIR, REDIS_URL


class ProfileMemory:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or (DATA_DIR / "profile.json")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._redis = None
        self._redis_key = "lab17:user_profile"
        self._lock = threading.Lock()
        if REDIS_URL:
            try:
                import redis

                self._redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None

    def load(self) -> dict[str, Any]:
        with self._lock:
            if self._redis is not None:
                raw = self._redis.get(self._redis_key)
                if raw:
                    return json.loads(raw)
                return {}
            if self._path.exists():
                return json.loads(self._path.read_text(encoding="utf-8"))
            return {}

    def save(self, data: dict[str, Any]) -> None:
        with self._lock:
            if self._redis is not None:
                self._redis.set(self._redis_key, json.dumps(data, ensure_ascii=False))
                return
            self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def merge(self, updates: dict[str, Any]) -> dict[str, Any]:
        """Fact mới ghi đè key cũ (conflict handling)."""
        current = self.load()
        for k, v in updates.items():
            if v is None:
                continue
            current[k] = v
        self.save(current)
        return current

    def reset(self) -> None:
        self.save({})
