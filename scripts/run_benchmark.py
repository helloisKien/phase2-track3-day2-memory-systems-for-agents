"""
Chạy 10 multi-turn scenarios (with-memory vs no-memory), in kết quả ra stdout.
Bạn chạy:  python scripts/run_benchmark.py
Yêu cầu: OPENAI_API_KEY trong .env hoặc môi trường.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from langchain_core.messages import AIMessage, HumanMessage

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.graph import build_graph  # noqa: E402
from src.memory.episodic_memory import EpisodicMemory  # noqa: E402
from src.memory.profile_memory import ProfileMemory  # noqa: E402


def load_scenarios(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data["scenarios"])


def run_scenario(graph, scenario: dict, memory_enabled: bool) -> list[str]:
    sid = f"scen_{scenario['id']}_{'mem' if memory_enabled else 'nomem'}"
    cfg = {"configurable": {"thread_id": sid, "memory_enabled": memory_enabled}}
    replies: list[str] = []
    for turn in scenario["turns"]:
        graph.invoke(
            {"messages": [HumanMessage(content=turn)], "memory_budget": 3500},
            config=cfg,
        )
        state = graph.get_state(cfg)
        vals = state.values
        msgs = vals.get("messages") or []
        last = msgs[-1] if msgs else None
        if isinstance(last, AIMessage):
            c = last.content
            replies.append(c if isinstance(c, str) else str(c))
        else:
            replies.append("")
    return replies


def main() -> None:
    scenarios_path = ROOT / "data" / "benchmark_scenarios.yaml"
    scenarios = load_scenarios(scenarios_path)
    graph = build_graph()
    profile = ProfileMemory()
    episodic = EpisodicMemory()

    rows = []
    for sc in scenarios:
        profile.reset()
        episodic.clear_file()
        with_mem = run_scenario(graph, sc, memory_enabled=True)
        profile.reset()
        episodic.clear_file()
        no_mem = run_scenario(graph, sc, memory_enabled=False)
        last_with = with_mem[-1] if with_mem else ""
        last_no = no_mem[-1] if no_mem else ""
        rows.append(
            {
                "id": sc["id"],
                "name": sc["name"],
                "group": sc["group"],
                "last_turn_no_memory": last_no[:500],
                "last_turn_with_memory": last_with[:500],
            }
        )

    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
