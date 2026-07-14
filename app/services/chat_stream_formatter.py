"""Chat SSE 格式化辅助。

【职责】
    把 event + data 转成 SSE 文本帧。

【SSE 格式】
    event: content_delta
    data: {"delta":"..."}

    每个事件后空一行，浏览器/客户端据此切分事件。
"""

import json
from collections.abc import Iterable

from app.core import constants
from app.schemas.agent_state import AgentState


def build_chat_sse_frames(state: AgentState) -> Iterable[str]:
    """根据最终 AgentState 构造最小 SSE 事件序列。

    参数:
        state: 最小图执行完成后的状态。

    返回:
        Iterable[str]: SSE 文本帧。
    """
    yield build_message_start_sse_frame(state)
    yield build_content_delta_sse_frame(state.answer)
    yield build_message_end_sse_frame(state)


def build_message_start_sse_frame(state: AgentState) -> str:
    """构造 message_start 事件帧。"""
    return format_sse_event(_start_event_data(state), constants.SSE_EVENT_MESSAGE_START)


def build_content_delta_sse_frame(delta: str) -> str:
    """构造 content_delta 事件帧。"""
    return format_sse_event({constants.SSE_FIELD_DELTA: delta}, constants.SSE_EVENT_CONTENT_DELTA)


def build_message_end_sse_frame(state: AgentState) -> str:
    """构造 message_end 事件帧。"""
    return format_sse_event(_end_event_data(state), constants.SSE_EVENT_MESSAGE_END)


def build_error_sse_frame(exc: Exception) -> str:
    """构造错误 SSE 事件。

    参数:
        exc: 被捕获的异常。

    返回:
        str: error 事件帧。
    """
    data = {
        constants.SSE_FIELD_ERROR_CODE: _read_error_code(exc),
        constants.SSE_FIELD_ERROR_MESSAGE: str(exc),
    }
    return format_sse_event(data, constants.SSE_EVENT_ERROR)


def build_usage_sse_frame(usage: dict) -> str:
    """构造 usage 事件帧。

    参数:
        usage: Provider 返回的 token 用量字典。

    返回:
        str: usage 事件帧。
    """
    return format_sse_event(usage, constants.SSE_EVENT_USAGE)


def build_status_sse_frame(phase: str) -> str:
    """构造 status 事件帧（thinking / generating）。"""
    data = {constants.SSE_FIELD_STATUS_PHASE: phase}
    return format_sse_event(data, constants.SSE_EVENT_STATUS)


def build_citation_sse_frame(citation: dict) -> str:
    """构造 citation 事件帧（Phase 2 检索接入后使用）。"""
    return format_sse_event(citation, constants.SSE_EVENT_CITATION)


def format_sse_event(data: dict, event: str) -> str:
    """格式化单个 SSE 事件。

    参数:
        data: 事件数据。
        event: 事件名。

    返回:
        str: 标准 SSE 文本。
    """
    json_data = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {json_data}\n\n"


def _read_error_code(exc: Exception) -> str:
    """从异常读取错误 code，缺省为 chat_error。"""
    raw_code = getattr(exc, "code", None)
    return raw_code if isinstance(raw_code, str) else constants.DEFAULT_SSE_ERROR_CODE


def _start_event_data(state: AgentState) -> dict:
    """构造 message_start 数据。"""
    return {constants.SSE_FIELD_CONVERSATION_ID: state.conversation_id}


def _end_event_data(state: AgentState) -> dict:
    """构造 message_end 数据。"""
    return {constants.SSE_FIELD_MESSAGE_IDS: state.message_ids}
