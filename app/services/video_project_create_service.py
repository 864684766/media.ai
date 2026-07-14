"""视频项目创建服务。"""

from sqlalchemy.orm import Session

from app.core.video_project_constants import PROJECT_STATUS_ACTIVE
from app.models.postgres.time_helper import utc_now
from app.models.postgres.video_project_model import VideoProjectModel
from app.schemas.video_project import VideoProjectCreateRequest, VideoProjectDetailResponse, VideoProjectOutput
from app.storage.postgres.video_project_repository import VideoProjectRepository
from app.video.project_id_slug_helper import is_valid_project_id, slug_from_title
from app.video.video_project_description_validator import normalize_project_description
from app.video.video_project_description_validator import normalize_project_description


class ProjectIdConflictError(Exception):
    """project_id 已存在。"""


class InvalidProjectIdError(Exception):
    """project_id 格式非法。"""


def create_video_project(
    session: Session,
    body: VideoProjectCreateRequest,
) -> VideoProjectDetailResponse:
    """创建 video_projects 记录。

    参数:
        session: DB Session。
        body: 创建请求。

    返回:
        VideoProjectDetailResponse: 含详情。

    异常:
        InvalidProjectIdError / ProjectIdConflictError。
    """
    project_id = _resolve_project_id(body)
    repo = VideoProjectRepository(session)
    if repo.get(project_id) is not None:
        raise ProjectIdConflictError(project_id)
    model = _build_model(project_id, body)
    saved = repo.insert(model)
    return _to_detail(saved, shot_count=0)


def _resolve_project_id(body: VideoProjectCreateRequest) -> str:
    """确定最终 project_id 并校验。"""
    project_id = body.project_id.strip() or slug_from_title(body.title)
    if not is_valid_project_id(project_id):
        raise InvalidProjectIdError(project_id)
    return project_id


def _build_model(project_id: str, body: VideoProjectCreateRequest) -> VideoProjectModel:
    """请求体转 ORM。"""
    now = utc_now()
    return VideoProjectModel(
        project_id=project_id,
        title=body.title.strip() or project_id,
        description=normalize_project_description(body.description),
        target_duration_sec=body.target_duration_sec,
        aspect_ratio=body.aspect_ratio,
        resolution=body.resolution,
        fps=body.fps,
        style_bible=body.style_bible,
        budget_limit_usd=body.budget_limit_usd,
        status=PROJECT_STATUS_ACTIVE,
        created_at=now,
        updated_at=now,
    )


def _to_detail(model: VideoProjectModel, shot_count: int) -> VideoProjectDetailResponse:
    """ORM 转详情响应。"""
    return VideoProjectDetailResponse(
        project=_to_output(model, shot_count),
        style_bible=model.style_bible,
    )


def _to_output(model: VideoProjectModel, shot_count: int) -> VideoProjectOutput:
    """ORM 转列表项。"""
    return VideoProjectOutput(
        project_id=model.project_id,
        title=model.title,
        description=model.description,
        status=model.status,
        aspect_ratio=model.aspect_ratio,
        resolution=model.resolution,
        fps=model.fps,
        budget_limit_usd=model.budget_limit_usd,
        shot_count=shot_count,
        updated_at=model.updated_at.isoformat() if model.updated_at else "",
    )
