"""创作大纲确认服务。"""

from sqlalchemy.orm import Session

from app.core.creative_plan_constants import PLAN_STATUS_APPROVED, PLAN_STATUS_AWAITING_REVIEW
from app.models.postgres.time_helper import utc_now
from app.schemas.creative_plan import CreativePlanItem
from app.services.creative_plan_errors import CreativePlanNotFoundError, CreativePlanStatusError
from app.services.creative_plan_mapper import map_plan_model
from app.storage.postgres.creative_plan_repository import CreativePlanRepository


def approve_creative_plan(session: Session, plan_id: str) -> CreativePlanItem:
    """锁定大纲为 approved。

    参数:
        session: SQLAlchemy Session。
        plan_id: 大纲 id。

    返回:
        CreativePlanItem: 确认后大纲。
    """
    row = CreativePlanRepository(session).get(plan_id)
    if row is None:
        raise CreativePlanNotFoundError(plan_id)
    if row.status != PLAN_STATUS_AWAITING_REVIEW:
        raise CreativePlanStatusError(f"当前状态 {row.status} 不可确认")
    now = utc_now()
    row.status = PLAN_STATUS_APPROVED
    row.approved_at = now
    row.updated_at = now
    saved = CreativePlanRepository(session).save(row)
    return map_plan_model(saved)
