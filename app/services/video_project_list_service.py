"""视频项目列表与详情服务。"""

from sqlalchemy.orm import Session

from app.core.video_project_constants import DEFAULT_PROJECT_LIST_LIMIT
from app.schemas.video_project import (
    ProjectSuggestionItem,
    ProjectSuggestionListResponse,
    VideoProjectDetailResponse,
    VideoProjectListResponse,
    VideoProjectOutput,
)
from app.storage.postgres.project_namespace_repository import collect_namespace_project_ids
from app.storage.postgres.shot_repository import ShotRepository
from app.storage.postgres.video_project_repository import VideoProjectRepository
from app.services.video_project_ensure_service import ensure_video_project_registered
from app.services.video_project_create_service import _to_detail, _to_output


def list_video_projects(session: Session, limit: int = DEFAULT_PROJECT_LIST_LIMIT) -> VideoProjectListResponse:
    """列出已注册项目。"""
    repo = VideoProjectRepository(session)
    shot_repo = ShotRepository(session)
    rows = repo.list_recent(limit)
    items = [_to_output(row, _shot_count(shot_repo, row.project_id)) for row in rows]
    return VideoProjectListResponse(items=items)


def get_video_project_detail(session: Session, project_id: str) -> VideoProjectDetailResponse | None:
    """查询单项目详情；命名空间已有 id 时惰性注册。"""
    row = VideoProjectRepository(session).get(project_id)
    if row is None:
        row = ensure_video_project_registered(session, project_id)
    if row is None:
        return None
    count = _shot_count(ShotRepository(session), project_id)
    return _to_detail(row, count)


def list_project_suggestions(session: Session) -> ProjectSuggestionListResponse:
    """聚合命名空间建议（含未注册 id）。"""
    repo = VideoProjectRepository(session)
    shot_repo = ShotRepository(session)
    registered = {row.project_id: row for row in repo.list_recent(200)}
    namespaces = collect_namespace_project_ids(session)
    all_ids = sorted(registered.keys() | namespaces)
    items = [_suggestion_item(pid, registered, shot_repo) for pid in all_ids]
    return ProjectSuggestionListResponse(items=items)


def _suggestion_item(pid: str, registered: dict, shot_repo: ShotRepository) -> ProjectSuggestionItem:
    """构造单条建议。"""
    row = registered.get(pid)
    return ProjectSuggestionItem(
        project_id=pid,
        registered=row is not None,
        title=row.title if row else "",
        description=row.description if row else "",
        shot_count=_shot_count(shot_repo, pid),
    )


def _shot_count(shot_repo: ShotRepository, project_id: str) -> int:
    """统计分镜数。"""
    return len(shot_repo.list_by_project(project_id))
