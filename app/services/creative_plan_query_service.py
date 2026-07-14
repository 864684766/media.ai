"""创作大纲查询服务。"""

from sqlalchemy.orm import Session

from app.schemas.creative_plan import CreativePlanItem, CreativePlanListResponse
from app.services.creative_plan_errors import CreativePlanNotFoundError
from app.services.creative_plan_mapper import map_plan_model
from app.storage.postgres.creative_plan_repository import CreativePlanRepository


def get_creative_plan(session: Session, plan_id: str) -> CreativePlanItem:
    """按 plan_id 查询大纲。

    参数:
        session: SQLAlchemy Session。
        plan_id: 主键。

    返回:
        CreativePlanItem: 大纲详情。
    """
    row = CreativePlanRepository(session).get(plan_id)
    if row is None:
        raise CreativePlanNotFoundError(plan_id)
    return map_plan_model(row)


def list_creative_plans_by_conversation(
    session: Session,
    conversation_id: str,
) -> CreativePlanListResponse:
    """查询会话下最新大纲列表（0–1 条）。

    参数:
        session: SQLAlchemy Session。
        conversation_id: 会话 id。

    返回:
        CreativePlanListResponse: 列表包装。
    """
    row = CreativePlanRepository(session).get_latest_by_conversation(conversation_id)
    if row is None:
        return CreativePlanListResponse(items=[])
    return CreativePlanListResponse(items=[map_plan_model(row)])
