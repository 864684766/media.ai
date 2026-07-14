"""视频生产线读写在 API 层。

【职责】
    V1：结构化分镜提交与按 project 列表。
    与 POST /chat 分工：chat 生成/讨论文本；本路由持久化 JSON。
"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_shot import (
    StoryboardListResponse,
    StoryboardSubmitRequest,
    StoryboardSubmitResponse,
)
from app.services.storyboard_service import list_project_shots, submit_storyboard
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 DATABASE_URL 时拒绝视频持久化接口。

    异常:
        HTTPException: 503 服务不可用。
    """
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL，无法使用视频分镜 API")


@router.post(
    "/projects/{project_id}/storyboard",
    summary="提交结构化分镜",
    response_model=StoryboardSubmitResponse,
)
def post_storyboard(
    project_id: str,
    body: StoryboardSubmitRequest,
) -> StoryboardSubmitResponse:
    """将 Shot JSON 数组写入 shots 表（默认全量替换同 project）。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return submit_storyboard(session, project_id, body)


@router.get(
    "/projects/{project_id}/shots",
    summary="列出项目分镜",
    response_model=StoryboardListResponse,
)
def get_project_shots(project_id: str) -> StoryboardListResponse:
    """按镜号返回 project 下已入库镜头。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return list_project_shots(session, project_id)
