"""CreativePlanModel → API 响应映射。"""

import json

from app.models.postgres.creative_plan_model import CreativePlanModel
from app.schemas.creative_plan import CreativePlanItem


def map_plan_model(model: CreativePlanModel) -> CreativePlanItem:
    """ORM 转 Pydantic 响应体。

    参数:
        model: 数据库行。

    返回:
        CreativePlanItem: API 契约对象。
    """
    content = _parse_content_json(model.content_json)
    return CreativePlanItem(
        plan_id=model.plan_id,
        conversation_id=model.conversation_id,
        project_id=model.project_id,
        creation_type=model.creation_type,
        status=model.status,
        version=model.version,
        title=model.title,
        content_json=content,
        content_md=model.content_md,
        user_feedback=model.user_feedback,
        clarification_session_id=model.clarification_session_id,
        revision_count=model.revision_count,
        created_at=model.created_at,
        updated_at=model.updated_at,
        approved_at=model.approved_at,
    )


def _parse_content_json(raw: str) -> dict:
    """安全解析 content_json。"""
    if not raw.strip():
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}
