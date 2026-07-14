"""compose_jobs Repository。"""

import uuid

from sqlalchemy.orm import Session

from app.core.video_constants import COMPOSE_JOB_STATUS_PENDING
from app.models.postgres.compose_job_model import ComposeJobModel
from app.models.postgres.time_helper import utc_now


class ComposeJobRepository:
    """合成任务读写。"""

    def __init__(self, session: Session) -> None:
        """绑定 Session。"""
        self._session = session

    def create_job(self, project_id: str, total_shots: int) -> ComposeJobModel:
        """创建 pending Job。"""
        job = ComposeJobModel(
            job_id=uuid.uuid4().hex,
            project_id=project_id,
            status=COMPOSE_JOB_STATUS_PENDING,
            total_shots=total_shots,
        )
        self._session.add(job)
        self._session.commit()
        self._session.refresh(job)
        return job

    def get_job(self, job_id: str) -> ComposeJobModel | None:
        """按 id 查询 Job。"""
        return self._session.get(ComposeJobModel, job_id)

    def mark_running(self, job: ComposeJobModel) -> None:
        """置为 running。"""
        from app.core.video_constants import COMPOSE_JOB_STATUS_RUNNING

        job.status = COMPOSE_JOB_STATUS_RUNNING
        job.updated_at = utc_now()
        self._session.commit()

    def mark_completed(
        self,
        job: ComposeJobModel,
        output_uri: str,
        timeline_json: str,
        subtitle_uri: str = "",
        audio_tracks_json: str = "",
    ) -> None:
        """置为 completed 并写入产物。"""
        from app.core.video_constants import COMPOSE_JOB_STATUS_COMPLETED

        job.status = COMPOSE_JOB_STATUS_COMPLETED
        job.output_uri = output_uri
        job.timeline_json = timeline_json
        job.subtitle_uri = subtitle_uri
        job.audio_tracks_json = audio_tracks_json
        job.updated_at = utc_now()
        self._session.commit()
