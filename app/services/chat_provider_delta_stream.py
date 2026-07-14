"""Provider delta 到 SSE frame 的转换器。

【职责】
    逐段读取 Provider delta，产出 content_delta SSE frame，并累计完整回答。
"""

from collections.abc import Generator

from app.graph.provider_stream_responder import stream_provider_answer_events
from app.schemas.agent_state import AgentState
from app.services.chat_stream_formatter import build_content_delta_sse_frame, build_usage_sse_frame


def yield_provider_delta_frames(state: AgentState) -> Generator[str, None, str]:
    """逐段输出 Provider delta frame，并在结束时返回完整回答。

    参数:
        state: 已准备好 prompt 的 AgentState。

    Yields:
        str: content_delta SSE frame。

    Returns:
        str: 拼接后的完整 assistant 回复。
    """
    chunks: list[str] = []
    for event in stream_provider_answer_events(state):
        if event.delta:
            chunks.append(event.delta)
            yield build_content_delta_sse_frame(event.delta)
        if event.usage:
            yield build_usage_sse_frame(event.usage)
    return "".join(chunks)
