"""创作大纲手工编辑服务。"""

from sqlalchemy.orm import Session

from app.core.creative_plan_constants import PLAN_STATUS_AWAITING_REVIEW
from app.models.postgres.time_helper import utc_now
from app.schemas.creative_plan import CreativePlanItem, CreativePlanPatchRequest
from app.services.creative_plan_errors import CreativePlanNotFoundError, CreativePlanStatusError
from app.services.creative_plan_mapper import map_plan_model
from app.storage.postgres.creative_plan_repository import CreativePlanRepository


def patch_creative_plan(
    session: Session,
    plan_id: str,
    body: CreativePlanPatchRequest,
) -> CreativePlanItem:
    """用户直接编辑 content_md。

    参数:
        session: SQLAlchemy Session。
        plan_id: 大纲 id。
        body: PATCH 请求体。

    返回:
        CreativePlanItem: 更新后大纲。
    """
    row = _require_awaiting_review(session, plan_id)
    row.content_md = body.content_md
    row.updated_at = utc_now()
    saved = CreativePlanRepository(session).save(row)
    return map_plan_model(saved)


def _require_awaiting_review(session: Session, plan_id: str):
    """加载且校验为待审状态。"""
    row = CreativePlanRepository(session).get(plan_id)
    if row is None:
        raise CreativePlanNotFoundError(plan_id)
    if row.status not in (PLAN_STATUS_AWAITING_REVIEW,):
        raise CreativePlanStatusError(f"当前状态 {row.status} 不可编辑")
    return row
