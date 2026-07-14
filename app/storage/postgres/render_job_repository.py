"""渲染 Job Repository。"""

import uuid

from sqlalchemy.orm import Session

from app.core.video_constants import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
)
from app.models.postgres.time_helper import utc_now
from app.models.postgres.video_render_job_model import VideoRenderJobModel


class RenderJobRepository:
    """video_render_jobs 读写。"""

    def __init__(self, session: Session) -> None:
        """绑定 Session。"""
        self._session = session

    def create_job(self, project_id: str, total_shots: int) -> VideoRenderJobModel:
        """创建 pending Job。"""
        job = VideoRenderJobModel(
            job_id=uuid.uuid4().hex,
            project_id=project_id,
            status=JOB_STATUS_PENDING,
            total_shots=total_shots,
            finished_shots=0,
        )
        self._session.add(job)
        self._session.commit()
        self._session.refresh(job)
        return job

    def get_job(self, job_id: str) -> VideoRenderJobModel | None:
        """按 id 查询 Job。"""
        return self._session.get(VideoRenderJobModel, job_id)

    def mark_running(self, job: VideoRenderJobModel) -> None:
        """置为 running。"""
        job.status = JOB_STATUS_RUNNING
        job.updated_at = utc_now()
        self._session.commit()

    def increment_finished(self, job: VideoRenderJobModel) -> None:
        """完成镜头数 +1。"""
        job.finished_shots += 1
        job.updated_at = utc_now()
        self._session.commit()

    def mark_completed(self, job: VideoRenderJobModel) -> None:
        """置为 completed。"""
        job.status = JOB_STATUS_COMPLETED
        job.updated_at = utc_now()
        self._session.commit()
