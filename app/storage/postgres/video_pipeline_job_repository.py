"""视频管线 Job Repository。"""

import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.video_pipeline_job_constants import PIPELINE_JOB_STATUS_PENDING
from app.models.postgres.time_helper import utc_now
from app.models.postgres.video_pipeline_job_model import VideoPipelineJobModel
from app.schemas.video_pipeline_state import VideoPipelineState


class VideoPipelineJobRepository:
    """video_pipeline_jobs 表读写。"""

    def __init__(self, session: Session) -> None:
        """绑定 Session。"""
        self._session = session

    def create_job(self, project_id: str, state: VideoPipelineState) -> VideoPipelineJobModel:
        """创建 pending Job。"""
        now = utc_now()
        row = VideoPipelineJobModel(
            job_id=str(uuid4()),
            project_id=project_id,
            status=PIPELINE_JOB_STATUS_PENDING,
            state_json=state.model_dump_json(),
            created_at=now,
            updated_at=now,
        )
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return row

    def get_job(self, job_id: str) -> VideoPipelineJobModel | None:
        """按 id 查询。"""
        return self._session.get(VideoPipelineJobModel, job_id)

    def save_checkpoint(self, job: VideoPipelineJobModel, state: VideoPipelineState, status: str) -> None:
        """写入 checkpoint。"""
        job.state_json = state.model_dump_json()
        job.status = status
        job.updated_at = utc_now()
        self._session.commit()

    def get_latest_job_for_project(self, project_id: str) -> VideoPipelineJobModel | None:
        """查询项目最近更新的 Job。"""
        return (
            self._session.query(VideoPipelineJobModel)
            .filter(VideoPipelineJobModel.project_id == project_id)
            .order_by(VideoPipelineJobModel.updated_at.desc())
            .first()
        )

    def load_state(self, job: VideoPipelineJobModel) -> VideoPipelineState:
        """从 Job 反序列化 state。"""
        data = json.loads(job.state_json or "{}")
        return VideoPipelineState.model_validate(data)
