"""已确认大纲注入 prompt。"""

from app.graph import prompt_constants as pc
from app.schemas.agent_state import AgentState
from app.core.outline_gate_constants import OUTLINE_PHASE_APPROVED
from app.services.approved_outline_loader import load_approved_outline_row


def inject_approved_outline(state: AgentState, db_session) -> AgentState:
    """将 approved 大纲写入 state.prompt 与 outline 字段。

    参数:
        state: 当前 AgentState。
        db_session: SQLAlchemy Session。

    返回:
        AgentState: 注入后状态；无 approved 时原样返回。
    """
    if db_session is None:
        return state
    row = load_approved_outline_row(db_session, state.conversation_id)
    if row is None or not row.content_md.strip():
        return state
    prompt = _append_outline_section(state.prompt, row.content_md)
    return state.model_copy(
        update={
            "prompt": prompt,
            "creative_plan_id": row.plan_id,
            "approved_outline_md": row.content_md,
            "outline_phase": OUTLINE_PHASE_APPROVED,
        },
    )


def _append_outline_section(prompt: str, outline_md: str) -> str:
    """在 prompt 末尾追加已确认大纲段落。"""
    section = f"{pc.PROMPT_SECTION_APPROVED_OUTLINE}\n{outline_md.strip()}"
    base = prompt.strip()
    if not base:
        return section
    return f"{base}{pc.PROMPT_PART_SEPARATOR}{section}"
