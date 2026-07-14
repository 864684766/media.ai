"""视频项目 PATCH 更新服务。"""

from sqlalchemy.orm import Session

from app.models.postgres.time_helper import utc_now
from app.schemas.video_project import VideoProjectDetailResponse, VideoProjectUpdateRequest
from app.services.video_project_ensure_service import ensure_video_project_registered
from app.services.video_project_create_service import _to_detail
from app.storage.postgres.shot_repository import ShotRepository
from app.storage.postgres.video_project_repository import VideoProjectRepository


class VideoProjectNotFoundError(Exception):
    """项目不存在。"""

    def __init__(self, project_id: str) -> None:
        """记录 project_id。"""
        super().__init__(project_id)
        self.project_id = project_id


def update_video_project(
    session: Session,
    project_id: str,
    body: VideoProjectUpdateRequest,
) -> VideoProjectDetailResponse:
    """更新项目可编辑字段（当前仅 style_bible）。

    参数:
        session: DB Session。
        project_id: 项目 id。
        body: PATCH 请求体。

    返回:
        VideoProjectDetailResponse: 更新后详情。

    异常:
        VideoProjectNotFoundError: 项目不存在。
    """
    repo = VideoProjectRepository(session)
    row = repo.get(project_id)
    if row is None:
        row = ensure_video_project_registered(session, project_id)
    if row is None:
        raise VideoProjectNotFoundError(project_id)
    _apply_patch(row, body)
    repo.commit()
    count = len(ShotRepository(session).list_by_project(project_id))
    return _to_detail(row, count)


def _apply_patch(row, body: VideoProjectUpdateRequest) -> None:
    """将 PATCH 字段写入 ORM。"""
    if body.style_bible is not None:
        row.style_bible = body.style_bible
        row.updated_at = utc_now()
