"""Semantic memory: Chroma nếu bật; fallback keyword overlap trên JSON chunks."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.config import CHROMA_PATH, DATA_DIR, USE_CHROMA


def _tokenize(text: str) -> set[str]:
    text = text.lower()
    return set(re.findall(r"[\wàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+", text))


class SemanticMemory:
    def __init__(self, chunks_path: Path | None = None) -> None:
        self._chunks_path = chunks_path or (DATA_DIR / "knowledge_chunks.json")
        self._collection = None
        self._client = None
        self._chroma_ids: list[str] = []
        self._load_chunks()
        if USE_CHROMA:
            self._try_chroma()

    def _load_chunks(self) -> None:
        raw = self._chunks_path.read_text(encoding="utf-8")
        self._chunks: list[dict[str, Any]] = json.loads(raw)

    def _try_chroma(self) -> None:
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            self._client = chromadb.PersistentClient(path=CHROMA_PATH)
            self._collection = self._client.get_or_create_collection(
                name="lab17_kb",
                embedding_function=embedding_functions.DefaultEmbeddingFunction(),
            )
            ids = set(self._collection.get()["ids"] or [])
            to_add_text: list[str] = []
            to_add_ids: list[str] = []
            to_add_meta: list[dict[str, Any]] = []
            for c in self._chunks:
                cid = str(c["id"])
                if cid not in ids:
                    to_add_ids.append(cid)
                    to_add_text.append(c["text"])
                    to_add_meta.append(dict(c.get("metadata") or {}))
            if to_add_ids:
                self._collection.add(ids=to_add_ids, documents=to_add_text, metadatas=to_add_meta)
        except Exception:
            self._collection = None
            self._client = None

    def search(self, query: str, k: int = 3) -> list[str]:
        if self._collection is not None:
            try:
                res = self._collection.query(query_texts=[query], n_results=k)
                docs = (res.get("documents") or [[]])[0]
                return [d for d in docs if d]
            except Exception:
                pass
        return self._keyword_search(query, k)

    def _keyword_search(self, query: str, k: int) -> list[str]:
        q = _tokenize(query)
        scored: list[tuple[int, str]] = []
        for c in self._chunks:
            t = _tokenize(c["text"])
            score = len(q & t)
            if score > 0:
                scored.append((score, c["text"]))
        scored.sort(key=lambda x: -x[0])
        return [s for _, s in scored[:k]]
