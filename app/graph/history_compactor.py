"""历史压缩编排。"""

from app.graph import history_constants as hc
from app.graph.history_summarizer import HistorySummarizer, TruncationSummarizer
from app.graph.history_summarizer_factory import build_history_summarizer
from app.graph.history_token_estimator import estimate_history_tokens
from app.schemas.agent_state import AgentState, ChatHistoryMessage

_default_summarizer: HistorySummarizer | TruncationSummarizer | None = None


def compact_history_if_needed(
    state: AgentState,
    summarizer: HistorySummarizer | TruncationSummarizer | None = None,
) -> AgentState:
    """超阈值时压缩历史并写入 history_summary。"""
    if estimate_history_tokens(state.history) <= hc.HISTORY_TOKEN_THRESHOLD:
        return state
    active = summarizer if summarizer is not None else _get_summarizer()
    older, recent = _split_history(state.history)
    summary = _merge_summary(state.history_summary, active.summarize(older))
    return state.model_copy(update={"history": recent, "history_summary": summary})


def _split_history(
    messages: list[ChatHistoryMessage],
) -> tuple[list[ChatHistoryMessage], list[ChatHistoryMessage]]:
    """拆成待摘要段与保留最近段。"""
    keep = hc.HISTORY_KEEP_RECENT_COUNT
    if len(messages) <= keep:
        return messages, []
    return messages[:-keep], messages[-keep:]


def _merge_summary(existing: str, fresh: str) -> str:
    """合并已有摘要与新摘要。"""
    if not fresh:
        return existing
    if not existing:
        return fresh
    return f"{existing}\n{fresh}"


def _get_summarizer() -> HistorySummarizer | TruncationSummarizer:
    """懒加载默认摘要器。"""
    global _default_summarizer
    if _default_summarizer is None:
        _default_summarizer = build_history_summarizer()
    return _default_summarizer
