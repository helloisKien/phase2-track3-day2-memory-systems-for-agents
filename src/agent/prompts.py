"""Prompt với 4 section: profile, episodic, semantic, recent conversation."""

from __future__ import annotations

import json
from typing import Any


def build_system_prompt(
    user_profile: dict[str, Any],
    episodes: list[dict[str, Any]],
    semantic_hits: list[str],
    recent_conversation: str,
) -> str:
    profile_block = json.dumps(user_profile, ensure_ascii=False, indent=2) if user_profile else "{}"
    episodic_lines = []
    for ep in episodes[-8:]:
        episodic_lines.append(f"- {ep}")
    episodic_block = "\n".join(episodic_lines) if episodic_lines else "(none)"
    semantic_block = "\n---\n".join(semantic_hits) if semantic_hits else "(none)"

    return f"""Bạn là trợ lý đa tác vụ. Chỉ dùng các khối memory bên dưới khi trả lời; nếu thiếu thông tin, nói rõ là không có trong memory.

### User profile (long-term)
{profile_block}

### Episodic memory (các sự kiện / bài học đã ghi)
{episodic_block}

### Semantic hits (đoạn kiến thức liên quan)
{semantic_block}

### Recent conversation (short-term buffer)
{recent_conversation}
"""


def estimate_tokens_tiktoken(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        import tiktoken

        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return max(1, len(text) // 4)


def apply_memory_budget(
    user_profile: dict[str, Any],
    episodes: list[dict[str, Any]],
    semantic_hits: list[str],
    recent_conversation: str,
    budget: int,
    model: str = "gpt-4o-mini",
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str], str, list[str]]:
    """
    Hierarchy eviction khi gần limit:
    1) Giảm semantic hits
    2) Rút episodic (ít episode hơn)
    3) Cắt recent conversation (giữ phần cuối)
    4) Profile chỉ giữ keys quan trọng
    Trả về (profile, episodes, semantic, recent, trim_log).
    """
    trim_log: list[str] = []
    sem = list(semantic_hits)
    eps = list(episodes)
    recent = recent_conversation
    prof = dict(user_profile)

    def total_size() -> int:
        blob = build_system_prompt(prof, eps, sem, recent)
        return estimate_tokens_tiktoken(blob, model=model)

    while total_size() > budget and len(sem) > 0:
        sem = sem[:-1]
        trim_log.append("drop_semantic_tail")

    while total_size() > budget and len(eps) > 1:
        eps = eps[1:]
        trim_log.append("drop_episode_head")

    while total_size() > budget and len(recent) > 400:
        recent = recent[len(recent) // 4 :]
        trim_log.append("shrink_recent_window")

    priority_keys = ["name", "allergy", "city"]
    while total_size() > budget and len(prof) > 0:
        keys = list(prof.keys())
        drop = next((k for k in keys if k not in priority_keys), None)
        if drop is None:
            # cuối cùng mới cắt priority theo thứ tự city -> name -> allergy
            for k in ["city", "name", "allergy"]:
                if k in prof:
                    del prof[k]
                    trim_log.append(f"drop_profile_{k}")
                    break
            else:
                break
        else:
            del prof[drop]
            trim_log.append(f"drop_profile_{drop}")

    return prof, eps, sem, recent, trim_log
