"""Kiểm tra offline: merge profile + conflict dị ứng (không gọi OpenAI). Chạy: python scripts/verify_profile_extraction.py"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agent.extraction import extract_profile_updates  # noqa: E402
from src.memory.profile_memory import ProfileMemory  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory() as d:
        p = ProfileMemory(path=Path(d) / "p.json")
        p.reset()
        u1 = extract_profile_updates("Tôi dị ứng sữa bò.")
        u2 = extract_profile_updates("À nhầm, tôi dị ứng đậu nành chứ không phải sữa bò.")
        p.merge(u1)
        p.merge(u2)
        allergy = p.load().get("allergy", "")
        print("allergy =", allergy.encode("unicode_escape").decode("ascii"))
        assert allergy, "expected allergy in profile"
        low = allergy.lower()
        assert "đậu" in low and "sữa bò" not in low
    print("OK: conflict handling profile.")


if __name__ == "__main__":
    main()
