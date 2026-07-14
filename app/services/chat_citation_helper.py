"""citation SSE 帧构造辅助。

【职责】
    把 state.retrieval.chunks 转成 citation 事件帧列表，
    事件数据结构与 docs/ARCHITECTURE.html sec-15「SSE 事件流」一致：
    { chunk_id, source, excerpt }。

【何时被调用】
    app/services/chat_stream_runner.py 在 message_start 之后、
    content_delta 之前逐条推送。
"""

from app.core import constants
from app.retrieval.retrieval_constants import CITATION_EXCERPT_MAX_CHARS
from app.schemas.agent_state import AgentState
from app.services.chat_stream_formatter import build_citation_sse_frame


def build_citation_frames(state: AgentState) -> list[str]:
    """构造本轮全部 citation 事件帧。

    参数:
        state: 已完成检索的 AgentState。

    返回:
        list[str]: citation SSE 帧列表；无检索证据时为空列表。
    """
    if state.retrieval is None:
        return []
    return [
        build_citation_sse_frame(
            {
                constants.SSE_FIELD_CITATION_CHUNK_ID: chunk.chunk_id,
                constants.SSE_FIELD_CITATION_SOURCE: chunk.source,
                constants.SSE_FIELD_CITATION_EXCERPT: _clip_excerpt(chunk.text),
            }
        )
        for chunk in state.retrieval.chunks
    ]


def _clip_excerpt(text: str) -> str:
    """截断证据文本作为摘要（避免 SSE 帧过大）。

    参数:
        text: chunk 原文。

    返回:
        str: 不超过 CITATION_EXCERPT_MAX_CHARS 的摘要。
    """
    if len(text) <= CITATION_EXCERPT_MAX_CHARS:
        return text
    return text[:CITATION_EXCERPT_MAX_CHARS]
