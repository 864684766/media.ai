"""创作大纲 AI 改稿服务（模板版 fallback）。"""

from sqlalchemy.orm import Session

from app.core.creative_config_reader import load_outline_config
from app.core.creative_plan_constants import PLAN_STATUS_AWAITING_REVIEW
from app.models.postgres.time_helper import utc_now
from app.schemas.creative_plan import CreativePlanItem, CreativePlanReviseRequest
from app.services.creative_plan_errors import (
    CreativePlanNotFoundError,
    CreativePlanRevisionLimitError,
    CreativePlanStatusError,
)
from app.services.creative_plan_mapper import map_plan_model
from app.storage.postgres.creative_plan_repository import CreativePlanRepository


def revise_creative_plan(
    session: Session,
    plan_id: str,
    body: CreativePlanReviseRequest,
) -> CreativePlanItem:
    """根据用户意见改稿并递增版本。

    参数:
        session: SQLAlchemy Session。
        plan_id: 大纲 id。
        body: 改稿意见。

    返回:
        CreativePlanItem: 新版本大纲。
    """
    cfg = load_outline_config()
    row = CreativePlanRepository(session).get(plan_id)
    if row is None:
        raise CreativePlanNotFoundError(plan_id)
    if row.status != PLAN_STATUS_AWAITING_REVIEW:
        raise CreativePlanStatusError(f"当前状态 {row.status} 不可改稿")
    if row.revision_count >= cfg.max_revisions:
        raise CreativePlanRevisionLimitError("改稿次数已达上限")
    row.user_feedback = body.comment.strip()
    row.content_md = _append_revision_note(row.content_md, body.comment)
    row.version += 1
    row.revision_count += 1
    row.updated_at = utc_now()
    saved = CreativePlanRepository(session).save(row)
    return map_plan_model(saved)


def _append_revision_note(content_md: str, comment: str) -> str:
    """在 Markdown 末尾追加改稿说明。"""
    note = comment.strip() or "（无具体意见，微调表述）"
    return f"{content_md.rstrip()}\n\n---\n\n**改稿说明**：{note}\n"
