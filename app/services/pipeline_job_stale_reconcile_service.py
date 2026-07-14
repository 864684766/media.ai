"""将过时的 paused Job 标记为 completed。"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_job_constants import PIPELINE_JOB_STATUS_COMPLETED
from app.core.video_pipeline_run_constants import PIPELINE_RUN_COMPLETED
from app.models.postgres.video_pipeline_job_model import VideoPipelineJobModel
from app.schemas.video_pipeline_state import VideoPipelineState
from app.storage.postgres.shot_repository import ShotRepository
from app.storage.postgres.video_pipeline_job_repository import VideoPipelineJobRepository
from app.video.pipeline_job_stale_reconciler import is_stale_bible_entity_pause
from app.video.pipeline_status_aggregator import aggregate_status_counts


def reconcile_stale_pipeline_job(session: Session, job: VideoPipelineJobModel) -> bool:
    """若 checkpoint 暂停原因已过时，则写入 completed 并返回 True。"""
    repo = VideoPipelineJobRepository(session)
    state = repo.load_state(job)
    counts = _load_status_counts(session, job.project_id)
    if not is_stale_bible_entity_pause(state, counts, sum(counts.values())):
        return False
    repo.save_checkpoint(job, _build_completed_state(state), PIPELINE_JOB_STATUS_COMPLETED)
    return True


def _load_status_counts(session: Session, project_id: str) -> dict[str, int]:
    """加载 project 镜头 status 计数。"""
    shots = ShotRepository(session).list_by_project(project_id)
    return aggregate_status_counts(shots)


def _build_completed_state(state: VideoPipelineState) -> VideoPipelineState:
    """构造 reconcile 后的 completed state。"""
    return state.model_copy(
        update={
            "run_status": PIPELINE_RUN_COMPLETED,
            "paused": False,
            "pause_reason": "",
            "error_message": "",
        },
    )
