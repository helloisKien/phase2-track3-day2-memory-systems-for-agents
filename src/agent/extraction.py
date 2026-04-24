"""Rule-based extraction cho profile + heuristic episodic."""

from __future__ import annotations

import re
from typing import Any


def _strip_allergy_fragment(frag: str) -> str:
    frag = frag.strip()
    for sep in [" chứ", " chứ không", " mà là", ".", "?", ";", "\n"]:
        if sep in frag:
            frag = frag.split(sep)[0].strip()
    return frag


def extract_profile_updates(text: str) -> dict[str, Any]:
    """Trích fact từ một lượt user; fact mới ghi đè qua merge ở ProfileMemory."""
    updates: dict[str, Any] = {}
    t = text.strip()

    mkey = re.search(r"PROFILE_KEY:\s*allergy\s*=\s*([^\s\.]+)", t, re.I)
    if mkey:
        updates["allergy"] = mkey.group(1).strip()

    if "dị ứng" in t.lower():
        m = re.search(r"dị ứng\s+([^\.\n\?]+)", t, re.I)
        if m:
            updates["allergy"] = _strip_allergy_fragment(m.group(1))

    for pat in [
        r"tên mình là\s+([^\.\n\?]+)",
        r"tên tôi là\s+([^\.\n\?]+)",
        r"gọi tôi là\s+([^\.\n\?]+)",
        r"tôi tên là\s+([^\.\n\?]+)",
    ]:
        m = re.search(pat, t, re.I)
        if m:
            updates["name"] = m.group(1).strip()
            break

    m = re.search(r"sống ở\s+([^\.\n\?]+)", t, re.I)
    if m:
        updates["city"] = m.group(1).strip()
    m = re.search(r"chuyển về\s+([^\.\n\?]+)", t, re.I)
    if m:
        updates["city"] = m.group(1).strip()

    return updates


def maybe_episode_from_user(text: str) -> dict[str, Any] | None:
    u = text.lower()
    if "deploy" in u and ("thành công" in u or "success" in u):
        return {"kind": "task_outcome", "summary": text.strip()[:800]}
    if "debug" in u and "docker" in u and ("localhost" in u or "service" in u or "bài học" in u):
        return {"kind": "lesson", "summary": text.strip()[:800]}
    return None
