"""Episodic memory: append-only JSONL log."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import DATA_DIR


class EpisodicMemory:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or (DATA_DIR / "episodes.jsonl")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def append(self, episode: dict[str, Any]) -> None:
        row = {"ts": datetime.now(timezone.utc).isoformat(), **episode}
        line = json.dumps(row, ensure_ascii=False) + "\n"
        with self._lock:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(line)

    def list_recent(self, n: int = 20) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        with self._lock:
            lines = self._path.read_text(encoding="utf-8").splitlines()
        out: list[dict[str, Any]] = []
        for line in lines[-n:]:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    def clear_file(self) -> None:
        with self._lock:
            if self._path.exists():
                self._path.unlink()
