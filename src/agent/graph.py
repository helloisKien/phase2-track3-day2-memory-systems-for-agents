"""LangGraph: retrieve_memory -> model (trim+prompt) -> save/update."""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from src.agent.extraction import extract_profile_updates, maybe_episode_from_user
from src.agent.prompts import apply_memory_budget, build_system_prompt, estimate_tokens_tiktoken
from src.agent.router import classify_intent
from src.config import OPENAI_MODEL
from src.memory.buffer_memory import ConversationBufferMemory
from src.memory.episodic_memory import EpisodicMemory
from src.memory.profile_memory import ProfileMemory
from src.memory.semantic_memory import SemanticMemory


class MemoryState(TypedDict):
    """Khớp rubric + messages cho LangGraph."""

    messages: Annotated[list[AnyMessage], add_messages]
    user_profile: dict[str, Any]
    episodes: list[dict[str, Any]]
    semantic_hits: list[str]
    memory_budget: int
    intent: str


def _last_human_text(messages: list[AnyMessage]) -> str:
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            c = m.content
            return c if isinstance(c, str) else str(c)
        if isinstance(m, BaseMessage) and getattr(m, "type", None) == "human":
            c = m.content
            return c if isinstance(c, str) else str(c)
    return ""


def _messages_to_recent_lines(messages: list[AnyMessage], max_pairs: int = 8) -> str:
    buf = ConversationBufferMemory(max_turns=max_pairs)
    buf.set_from_langchain_messages(messages)
    return buf.as_chat_lines()


def build_graph():
    profile_mem = ProfileMemory()
    episodic_mem = EpisodicMemory()
    semantic_mem = SemanticMemory()

    def retrieve_memory(state: MemoryState, config: RunnableConfig) -> dict[str, Any]:
        cfg = config.get("configurable") or {}
        enabled = cfg.get("memory_enabled", True)
        text = _last_human_text(state["messages"])
        intent = classify_intent(text)
        if not enabled:
            return {
                "intent": intent,
                "user_profile": {},
                "episodes": [],
                "semantic_hits": [],
            }
        full_profile = profile_mem.load()
        if intent == "user_preference":
            eps_n, sem_k = 8, 1
        elif intent == "factual_recall":
            eps_n, sem_k = 2, 4
        elif intent == "experience_recall":
            eps_n, sem_k = 15, 1
        else:
            eps_n, sem_k = 6, 3
        eps = episodic_mem.list_recent(eps_n)
        sem = semantic_mem.search(text, k=sem_k) if text else []
        return {
            "intent": intent,
            "user_profile": full_profile,
            "episodes": eps,
            "semantic_hits": sem,
        }

    def call_model(state: MemoryState, config: RunnableConfig) -> dict[str, Any]:
        cfg = config.get("configurable") or {}
        model_name = cfg.get("openai_model", OPENAI_MODEL)
        budget = int(state.get("memory_budget") or 4000)
        recent = _messages_to_recent_lines(state["messages"])
        prof, eps, sem, recent_trimmed, _trim_log = apply_memory_budget(
            state.get("user_profile") or {},
            state.get("episodes") or [],
            state.get("semantic_hits") or [],
            recent,
            budget=budget,
            model=model_name,
        )
        system = build_system_prompt(prof, eps, sem, recent_trimmed)
        llm = ChatOpenAI(model=model_name, temperature=0.2)
        msgs = [SystemMessage(content=system), *state["messages"]]
        resp = llm.invoke(msgs)
        content = resp.content if isinstance(resp.content, str) else str(resp.content)
        return {"messages": [AIMessage(content=content)]}

    def save_memory(state: MemoryState, config: RunnableConfig) -> dict[str, Any]:
        cfg = config.get("configurable") or {}
        if not cfg.get("memory_enabled", True):
            return {}
        text = _last_human_text(state["messages"])
        if not text:
            return {}
        updates = extract_profile_updates(text)
        if updates:
            profile_mem.merge(updates)
        ep = maybe_episode_from_user(text)
        if ep:
            episodic_mem.append(ep)
        return {}

    g = StateGraph(MemoryState)
    g.add_node("retrieve_memory", retrieve_memory)
    g.add_node("model", call_model)
    g.add_node("save_memory", save_memory)
    g.add_edge(START, "retrieve_memory")
    g.add_edge("retrieve_memory", "model")
    g.add_edge("model", "save_memory")
    g.add_edge("save_memory", END)
    checkpointer = MemorySaver()
    return g.compile(checkpointer=checkpointer)


def token_breakdown_for_messages(messages: list[AnyMessage], model: str = OPENAI_MODEL) -> dict[str, int]:
    """Tiện ích cho benchmark: ước lượng token theo phần."""
    recent = _messages_to_recent_lines(messages)
    return {
        "recent_chars": len(recent),
        "recent_tokens_est": estimate_tokens_tiktoken(recent, model=model),
    }
