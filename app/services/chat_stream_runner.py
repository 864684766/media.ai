"""Chat SSE 执行器。

【职责】
    准备 state（含可选检索），推送 citation，调用 Provider 流式输出，
    并把异常转成 SSE error 事件。

【事件顺序】
    status(thinking) → [准备图] → message_start → citation* → status(generating)
    → content_delta* → message_end
"""

from collections.abc import Iterable

from app.graph.route_classifiers import RouteClassifiers
from app.graph.nodes.save_messages import save_messages_node
from app.graph.stream_state_preparer import prepare_stream_state
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.schemas.chat import ChatRequest
from app.services.chat_citation_helper import build_citation_frames
from app.services.chat_provider_delta_stream import yield_provider_delta_frames
from app.services.clarification_stream_service import try_clarification_stream
from app.services.approved_outline_prompt_injector import inject_approved_outline
from app.services.outline_gate_stream_service import try_outline_gate_stream
from app.core import constants
from app.services.chat_stream_formatter import (
    build_error_sse_frame,
    build_message_end_sse_frame,
    build_message_start_sse_frame,
    build_status_sse_frame,
)
from app.storage.postgres.conversation_repository import ConversationRepository


def stream_chat_frames(
    request: ChatRequest,
    repository: ConversationRepository | None,
    retrieval_pipeline: RetrievalPipeline | None = None,
    route_classifiers: RouteClassifiers | None = None,
) -> Iterable[str]:
    """执行图并返回 SSE 帧。

    参数:
        request: Chat API 请求体。
        repository: 可选 PG Repository。
        retrieval_pipeline: 可选检索流水线；证据以 citation 事件推送。
        route_classifiers: 可选路由级联分类器包。

    返回:
        Iterable[str]: SSE 帧。
    """
    try:
        yield build_status_sse_frame(constants.STATUS_PHASE_THINKING)
        state = prepare_stream_state(
            request,
            repository,
            retrieval_pipeline,
            route_classifiers=route_classifiers,
        )
        yield build_message_start_sse_frame(state)
        db_session = repository.db_session if repository is not None else None
        clarify = try_clarification_stream(request, state, db_session)
        if clarify is not None:
            for frame in clarify.frames:
                yield frame
            saved_state = save_messages_node(clarify.state, repository=repository)
            yield build_message_end_sse_frame(saved_state)
            return
        gate = try_outline_gate_stream(request, state, db_session)
        if gate is not None:
            for frame in gate.frames:
                yield frame
            saved_state = save_messages_node(gate.state, repository=repository)
            yield build_message_end_sse_frame(saved_state)
            return
        state = inject_approved_outline(state, db_session)
        yield from build_citation_frames(state)
        yield build_status_sse_frame(constants.STATUS_PHASE_GENERATING)
        answer = yield from yield_provider_delta_frames(state)
        final_state = state.model_copy(update={"answer": answer})
        saved_state = save_messages_node(final_state, repository=repository)
        yield build_message_end_sse_frame(saved_state)
    except Exception as exc:  # noqa: BLE001 — SSE 接口需把异常转成 error 事件
        yield build_error_sse_frame(exc)
