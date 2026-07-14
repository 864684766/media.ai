"""视频 E2E 演示 G2 路径：策划→分镜。"""

import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.creative_plan_constants import PLAN_STATUS_APPROVED
from app.core.creation_type_constants import CREATION_TYPE_VIDEO
from app.models.postgres.creative_plan_model import CreativePlanModel
from app.models.postgres.time_helper import utc_now
from app.schemas.creative_plan import CreativePlanStoryboardRequest, VideoPlanContent, VideoSegmentItem
from app.services.creative_plan_storyboard_service import generate_storyboard_from_approved_plan


def run_demo_plan_storyboard(session: Session, project_id: str) -> dict:
    """插入 approved 视频大纲并调用 G2 生成分镜。

    参数:
        session: PG Session。
        project_id: 目标项目 id。

    返回:
        dict: G2 响应摘要。
    """
    plan_id = _insert_approved_plan(session, project_id)
    response = generate_storyboard_from_approved_plan(
        session,
        plan_id,
        CreativePlanStoryboardRequest(project_id=project_id),
    )
    return response.model_dump()


def _insert_approved_plan(session: Session, project_id: str) -> str:
    """写入一条 approved 视频策划案。"""
    content = VideoPlanContent(
        hook="E2E 产品开场",
        segments=[
            VideoSegmentItem(start_sec=0, end_sec=5, visual="产品特写", mood="期待"),
            VideoSegmentItem(start_sec=5, end_sec=15, visual="功能演示", mood="上扬"),
        ],
        target_duration_sec=15,
    )
    now = utc_now()
    plan_id = str(uuid4())
    row = CreativePlanModel(
        plan_id=plan_id,
        conversation_id=str(uuid4()),
        project_id=project_id,
        creation_type=CREATION_TYPE_VIDEO,
        status=PLAN_STATUS_APPROVED,
        version=1,
        title="E2E 视频方案",
        content_json=json.dumps(content.model_dump(), ensure_ascii=False),
        content_md="## 开场\n产品特写",
        clarification_session_id=None,
        created_at=now,
        updated_at=now,
        approved_at=now,
    )
    session.add(row)
    session.flush()
    return plan_id
