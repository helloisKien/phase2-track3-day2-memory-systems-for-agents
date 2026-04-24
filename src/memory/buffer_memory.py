"""Short-term memory: sliding window over recent turns (conversation buffer)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversationBufferMemory:
    """Giữ tối đa `max_turns` cặp user/assistant (ước lượng theo số message)."""

    max_turns: int = 12
    _messages: list[dict[str, Any]] = field(default_factory=list)

    def add_messages(self, messages: list[dict[str, Any]]) -> None:
        self._messages.extend(messages)
        self._trim()

    def set_from_langchain_messages(self, messages: list[Any]) -> None:
        """Chuyển LangChain messages thành dict đơn giản để đếm buffer."""
        self._messages.clear()
        for m in messages:
            if isinstance(m, dict):
                role = m.get("role", "user")
                content = m.get("content")
            else:
                t = getattr(m, "type", None)
                if t == "human":
                    role = "user"
                elif t == "ai":
                    role = "assistant"
                elif t == "system":
                    continue
                else:
                    role = "user"
                content = getattr(m, "content", None)
            if role == "human":
                role = "user"
            if role == "ai":
                role = "assistant"
            if content is not None:
                self._messages.append({"role": role, "content": str(content)})
        self._trim()

    def _trim(self) -> None:
        # Giữ ~ max_turns * 2 messages (user+assistant)
        cap = max(1, self.max_turns * 2)
        if len(self._messages) > cap:
            self._messages = self._messages[-cap:]

    def as_chat_lines(self) -> str:
        if not self._messages:
            return "(empty)"
        lines = []
        for m in self._messages:
            lines.append(f"{m['role']}: {m['content']}")
        return "\n".join(lines)

    def clear(self) -> None:
        self._messages.clear()
