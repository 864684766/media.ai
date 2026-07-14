"""命名空间 project_id 惰性注册 video_projects。"""

from sqlalchemy.orm import Session

from app.core.video_project_constants import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_PROJECT_FPS,
    DEFAULT_RESOLUTION,
    DEFAULT_TARGET_DURATION_SEC,
    PROJECT_STATUS_ACTIVE,
)
from app.models.postgres.time_helper import utc_now
from app.models.postgres.video_project_model import VideoProjectModel
from app.storage.postgres.project_namespace_repository import project_id_in_namespace
from app.storage.postgres.video_project_repository import VideoProjectRepository
from app.video.project_id_slug_helper import is_valid_project_id


def ensure_video_project_registered(session: Session, project_id: str) -> VideoProjectModel | None:
    """命名空间已有 id 时补建 video_projects（供 style_bible 等读写）。

    参数:
        session: DB Session。
        project_id: 项目 slug。

    返回:
        VideoProjectModel | None: 已存在或新注册；不可注册时 None。
    """
    repo = VideoProjectRepository(session)
    existing = repo.get(project_id)
    if existing is not None:
        return existing
    if not _can_auto_register(session, project_id):
        return None
    return repo.insert(_build_default_model(project_id))


def _can_auto_register(session: Session, project_id: str) -> bool:
    """判断是否允许惰性注册。"""
    if not is_valid_project_id(project_id):
        return False
    return project_id_in_namespace(session, project_id)


def _build_default_model(project_id: str) -> VideoProjectModel:
    """构造最小默认项目 ORM。"""
    now = utc_now()
    return VideoProjectModel(
        project_id=project_id,
        title=project_id,
        description="",
        target_duration_sec=DEFAULT_TARGET_DURATION_SEC,
        aspect_ratio=DEFAULT_ASPECT_RATIO,
        resolution=DEFAULT_RESOLUTION,
        fps=DEFAULT_PROJECT_FPS,
        style_bible="",
        budget_limit_usd=0.0,
        status=PROJECT_STATUS_ACTIVE,
        created_at=now,
        updated_at=now,
    )
