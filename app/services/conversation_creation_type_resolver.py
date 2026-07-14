"""会话 creation_type 解析（历史会话推断）。

【职责】
    优先读 conversations.creation_type；缺失时从 creative_plans / clarification_sessions 推断。

【何时调用】
    GET /conversations、GET /conversations/{id}/messages 组装响应时。
"""

from sqlalchemy.orm import Session

from app.core.creation_type_constants import CREATION_TYPE_NOVEL, CREATION_TYPE_VIDEO
from app.models.postgres.conversation_model import ConversationModel
from app.storage.postgres.clarification_session_repository import ClarificationSessionRepository
from app.storage.postgres.creative_plan_repository import CreativePlanRepository


def resolve_conversation_creation_type(
    session: Session,
    conversation_id: str,
) -> str:
    """解析会话绑定的创作类型。

    参数:
        session: SQLAlchemy Session。
        conversation_id: 会话 id。

    返回:
        str: novel | video。
    """
    stored = _read_stored_type(session, conversation_id)
    if stored is not None:
        return stored
    inferred = _infer_from_related_tables(session, conversation_id)
    if inferred is not None:
        return inferred
    return CREATION_TYPE_NOVEL


def _read_stored_type(session: Session, conversation_id: str) -> str | None:
    """读取 conversations 表已存 creation_type。"""
    row = session.get(ConversationModel, conversation_id)
    if row is None or not row.creation_type:
        return None
    value = row.creation_type.strip()
    if value in (CREATION_TYPE_NOVEL, CREATION_TYPE_VIDEO):
        return value
    return None


def _infer_from_related_tables(session: Session, conversation_id: str) -> str | None:
    """从大纲或澄清会话推断类型。"""
    plan = CreativePlanRepository(session).get_latest_by_conversation(conversation_id)
    if plan is not None and plan.creation_type:
        return plan.creation_type
    clarify = ClarificationSessionRepository(session).get_latest_by_conversation(conversation_id)
    if clarify is not None and clarify.creation_type:
        return clarify.creation_type
    return None
