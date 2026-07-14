"""已确认大纲加载（注入 prompt 用）。"""

from sqlalchemy.orm import Session

from app.core.creative_plan_constants import PLAN_STATUS_APPROVED
from app.core.outline_gate_constants import OUTLINE_PHASE_APPROVED, OUTLINE_PHASE_NONE, OUTLINE_PHASE_PROPOSED
from app.storage.postgres.creative_plan_repository import CreativePlanRepository


def load_approved_outline_row(session: Session, conversation_id: str):
    """加载会话下 approved 大纲 ORM 行。

    参数:
        session: SQLAlchemy Session。
        conversation_id: 会话 id。

    返回:
        CreativePlanModel | None: 已确认大纲；无则 None。
    """
    return CreativePlanRepository(session).get_approved_by_conversation(conversation_id)


def resolve_outline_phase(session: Session | None, conversation_id: str) -> str:
    """解析会话大纲阶段（none / proposed / approved）。

    参数:
        session: 可选 DB Session。
        conversation_id: 会话 id。

    返回:
        str: outline_phase 取值。
    """
    if session is None:
        return OUTLINE_PHASE_NONE
    repo = CreativePlanRepository(session)
    if repo.get_approved_by_conversation(conversation_id) is not None:
        return OUTLINE_PHASE_APPROVED
    latest = repo.get_latest_by_conversation(conversation_id)
    if latest is None:
        return OUTLINE_PHASE_NONE
    if latest.status == PLAN_STATUS_APPROVED:
        return OUTLINE_PHASE_APPROVED
    return OUTLINE_PHASE_PROPOSED
