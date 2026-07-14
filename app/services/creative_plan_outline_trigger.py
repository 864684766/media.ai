"""澄清完成后自动触发大纲生成。

【职责】
    阶段 F 结束后若 outline.enabled，创建 creative_plan 并返回 SSE 帧。

【简例】
    frame = try_build_outline_proposed_frame(db_session, conversation_id, session_id, ...)
"""

from sqlalchemy.orm import Session

from app.core.creative_config_reader import load_outline_config
from app.schemas.creative_plan import CreativePlanCreateRequest
from app.services.creative_plan_create_service import create_creative_plan
from app.services.outline_sse_frame_builder import build_outline_proposed_frame
from app.storage.postgres.creative_plan_repository import CreativePlanRepository


def try_build_outline_proposed_frame(
    db_session: Session,
    conversation_id: str,
    project_id: str | None,
    creation_type: str,
    clarification_session_id: str,
) -> str | None:
    """尝试自动创建大纲并返回 outline_proposed SSE 帧。

    参数:
        db_session: SQLAlchemy Session。
        conversation_id: 会话 id。
        project_id: 可选项目 id。
        creation_type: novel | video。
        clarification_session_id: 刚完成的澄清会话 id。

    返回:
        str | None: SSE 帧；未启用或已有 approved 时 None。
    """
    cfg = load_outline_config()
    if not cfg.enabled:
        return None
    repo = CreativePlanRepository(db_session)
    if repo.has_approved_for_conversation(conversation_id):
        return None
    body = CreativePlanCreateRequest(
        conversation_id=conversation_id,
        project_id=project_id,
        creation_type=creation_type,
        clarification_session_id=clarification_session_id,
    )
    plan = create_creative_plan(db_session, body)
    return build_outline_proposed_frame(plan)
