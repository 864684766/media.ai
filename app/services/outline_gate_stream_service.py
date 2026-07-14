"""大纲闸门 SSE 分支（阶段 G）。

【职责】
    未确认大纲时拦截 Provider，返回固定引导文案。

【简例】
    outcome = try_outline_gate_stream(request, state, db_session)
    if outcome: yield frames; save; return
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.creative_config_reader import load_outline_config
from app.core.outline_gate_constants import OUTLINE_GATE_BLOCK_MESSAGE
from app.creative.outline_gate_detector import should_enforce_outline_gate
from app.schemas.agent_state import AgentState
from app.schemas.chat import ChatRequest
from app.services.approved_outline_loader import load_approved_outline_row
from app.services.chat_stream_formatter import build_content_delta_sse_frame


@dataclass(frozen=True)
class OutlineGateOutcome:
    """大纲闸门 SSE 输出。"""

    frames: tuple[str, ...]
    state: AgentState


def try_outline_gate_stream(
    request: ChatRequest,
    state: AgentState,
    db_session: Session | None,
) -> OutlineGateOutcome | None:
    """未确认大纲时拦截生成；适用时返回 SSE 帧。

    参数:
        request: Chat 请求。
        state: 已准备 state。
        db_session: 可选 PG Session。

    返回:
        OutlineGateOutcome | None: 拦截时返回帧；否则 None 继续生成。
    """
    cfg = load_outline_config()
    if not should_enforce_outline_gate(request, state, cfg):
        return None
    if db_session is None:
        return None
    if load_approved_outline_row(db_session, state.conversation_id) is not None:
        return None
    frame = build_content_delta_sse_frame(OUTLINE_GATE_BLOCK_MESSAGE)
    answer = OUTLINE_GATE_BLOCK_MESSAGE
    return OutlineGateOutcome(frames=(frame,), state=state.model_copy(update={"answer": answer}))
