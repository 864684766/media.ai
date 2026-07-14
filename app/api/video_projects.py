"""视频项目 API（CRUD + 建议列表）。"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_project import (
    ProjectSuggestionListResponse,
    VideoProjectCreateRequest,
    VideoProjectDetailResponse,
    VideoProjectListResponse,
    VideoProjectUpdateRequest,
)
from app.services.video_project_create_service import (
    InvalidProjectIdError,
    ProjectIdConflictError,
    create_video_project,
)
from app.services.video_project_update_service import (
    VideoProjectNotFoundError,
    update_video_project,
)
from app.video.video_project_description_validator import ProjectDescriptionTooLongError
from app.services.video_project_list_service import (
    get_video_project_detail,
    list_project_suggestions,
    list_video_projects,
)
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 PG 时 503。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")


@router.get("/projects/suggestions", summary="项目命名空间建议", response_model=ProjectSuggestionListResponse)
def get_project_suggestions() -> ProjectSuggestionListResponse:
    """聚合 shots/documents/conversations 与已注册项目。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return list_project_suggestions(session)


@router.get("/projects", summary="视频项目列表", response_model=VideoProjectListResponse)
def get_video_projects() -> VideoProjectListResponse:
    """返回已注册 video_projects（按更新时间倒序）。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return list_video_projects(session)


@router.post("/projects", summary="创建视频项目", response_model=VideoProjectDetailResponse)
def post_create_video_project(body: VideoProjectCreateRequest) -> VideoProjectDetailResponse:
    """创建项目元数据（不等同于提交分镜）。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            return create_video_project(session, body)
    except InvalidProjectIdError as exc:
        raise HTTPException(status_code=400, detail=f"非法 project_id: {exc}") from exc
    except ProjectIdConflictError as exc:
        raise HTTPException(status_code=409, detail=f"project_id 已存在: {exc}") from exc
    except ProjectDescriptionTooLongError as exc:
        raise HTTPException(status_code=400, detail=f"description 超过最大长度: {exc}") from exc


@router.get("/projects/{project_id}", summary="视频项目详情", response_model=VideoProjectDetailResponse)
def get_video_project(project_id: str) -> VideoProjectDetailResponse:
    """查询单项目；命名空间已有 id 时自动补注册。"""
    _require_postgres()
    with postgres_session_scope() as session:
        detail = get_video_project_detail(session, project_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    return detail


@router.patch("/projects/{project_id}", summary="更新视频项目", response_model=VideoProjectDetailResponse)
def patch_video_project(
    project_id: str,
    body: VideoProjectUpdateRequest,
) -> VideoProjectDetailResponse:
    """更新 style_bible 等可编辑字段。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            return update_video_project(session, project_id, body)
    except VideoProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"项目不存在: {exc.project_id}") from exc
