"""创作大纲创建服务。"""

import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.creative_config_reader import load_outline_config
from app.core.creative_plan_constants import (
    PLAN_INITIAL_VERSION,
    PLAN_STATUS_APPROVED,
    PLAN_STATUS_AWAITING_REVIEW,
)
from app.creative.outline_content_md_renderer import render_content_md
from app.creative.outline_template_builder import build_outline_content, build_outline_title
from app.models.postgres.creative_plan_model import CreativePlanModel
from app.models.postgres.time_helper import utc_now
from app.schemas.creative_plan import CreativePlanCreateRequest, CreativePlanItem
from app.services.creative_plan_errors import ClarificationRequiredError
from app.services.creative_plan_mapper import map_plan_model
from app.storage.postgres.clarification_session_repository import ClarificationSessionRepository
from app.storage.postgres.creative_plan_repository import CreativePlanRepository


def create_creative_plan(session: Session, body: CreativePlanCreateRequest) -> CreativePlanItem:
    """根据澄清摘要或 brief 创建大纲 v1。

    参数:
        session: SQLAlchemy Session。
        body: 创建请求。

    返回:
        CreativePlanItem: 新大纲详情。
    """
    cfg = load_outline_config()
    summary_md = _resolve_summary(session, body, cfg.requires_clarification)
    content = build_outline_content(body.creation_type, summary_md)
    content_md = render_content_md(body.creation_type, content)
    model = _build_model(body, content, content_md)
    if cfg.auto_approve:
        model.status = PLAN_STATUS_APPROVED
        model.approved_at = utc_now()
    saved = CreativePlanRepository(session).insert(model)
    return map_plan_model(saved)


def _resolve_summary(session: Session, body: CreativePlanCreateRequest, requires: bool) -> str:
    """解析用于生成大纲的摘要文本。"""
    if body.clarification_session_id:
        row = ClarificationSessionRepository(session).get(body.clarification_session_id)
        if row and row.requirements_summary.strip():
            return row.requirements_summary
    latest = ClarificationSessionRepository(session).get_latest_completed_by_conversation(
        body.conversation_id,
    )
    if latest and latest.requirements_summary.strip():
        return latest.requirements_summary
    if requires:
        raise ClarificationRequiredError("需要先完成澄清引导")
    return body.brief or "用户未提供详细 brief，使用默认模板大纲。"


def _build_model(
    body: CreativePlanCreateRequest,
    content: dict,
    content_md: str,
) -> CreativePlanModel:
    """构造待插入 ORM。"""
    now = utc_now()
    return CreativePlanModel(
        plan_id=str(uuid4()),
        conversation_id=body.conversation_id,
        project_id=body.project_id,
        creation_type=body.creation_type,
        status=PLAN_STATUS_AWAITING_REVIEW,
        version=PLAN_INITIAL_VERSION,
        title=build_outline_title(body.creation_type),
        content_json=json.dumps(content, ensure_ascii=False),
        content_md=content_md,
        clarification_session_id=body.clarification_session_id,
        created_at=now,
        updated_at=now,
    )
