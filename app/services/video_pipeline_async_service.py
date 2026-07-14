"""视频管线异步 Job 业务服务（阶段 D3）。"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_job_constants import (
    PIPELINE_JOB_STATUS_COMPLETED,
    PIPELINE_JOB_STATUS_FAILED,
    PIPELINE_JOB_STATUS_PAUSED,
    PIPELINE_JOB_STATUS_RUNNING,
)
from app.core.video_pipeline_run_constants import (
    PIPELINE_RUN_COMPLETED,
    PIPELINE_RUN_PAUSED,
    PIPELINE_RUN_PENDING,
)
from app.schemas.video_pipeline_job import VideoPipelineJobDetailResponse
from app.schemas.video_pipeline_run import VideoPipelineRunResponse
from app.schemas.video_pipeline_state import VideoPipelineState
from app.services.pipeline_job_stale_reconcile_service import reconcile_stale_pipeline_job
from app.services.video_pipeline_checkpoint_runner import (
    resolve_resume_step_index,
    run_pipeline_from_step_index,
)
from app.services.video_pipeline_run_mapper import map_pipeline_run_response
from app.storage.postgres.video_pipeline_job_repository import VideoPipelineJobRepository


class PipelineJobNotFoundError(Exception):
    """Job 不存在。"""

    def __init__(self, job_id: str) -> None:
        """记录 job_id。"""
        super().__init__(job_id)
        self.job_id = job_id


def start_async_pipeline_job(session: Session, project_id: str) -> str:
    """创建 Job 并返回 job_id（由 worker 线程执行）。"""
    initial = VideoPipelineState(project_id=project_id, run_status=PIPELINE_RUN_PENDING)
    row = VideoPipelineJobRepository(session).create_job(project_id, initial)
    return row.job_id


def execute_pipeline_job(session: Session, job_id: str) -> VideoPipelineRunResponse:
    """同步执行 Job 全步骤（测试与 worker 共用）。"""
    repo = VideoPipelineJobRepository(session)
    job = repo.get_job(job_id)
    if job is None:
        raise PipelineJobNotFoundError(job_id)
    state = repo.load_state(job)
    repo.save_checkpoint(job, state, PIPELINE_JOB_STATUS_RUNNING)
    final_state = run_pipeline_from_step_index(session, state, 0)
    status = _resolve_job_status(final_state)
    repo.save_checkpoint(job, final_state, status)
    return map_pipeline_run_response(final_state)


def resume_pipeline_job(session: Session, job_id: str) -> VideoPipelineRunResponse:
    """从 checkpoint 续跑 Job。"""
    repo = VideoPipelineJobRepository(session)
    job = repo.get_job(job_id)
    if job is None:
        raise PipelineJobNotFoundError(job_id)
    state = repo.load_state(job)
    state = state.model_copy(update={"paused": False, "pause_reason": "", "error_message": ""})
    start_index = resolve_resume_step_index(state)
    repo.save_checkpoint(job, state, PIPELINE_JOB_STATUS_RUNNING)
    final_state = run_pipeline_from_step_index(session, state, start_index)
    status = _resolve_job_status(final_state)
    repo.save_checkpoint(job, final_state, status)
    return map_pipeline_run_response(final_state)


def get_pipeline_job_status(session: Session, job_id: str) -> VideoPipelineRunResponse:
    """查询 Job 当前 checkpoint。"""
    repo = VideoPipelineJobRepository(session)
    job = repo.get_job(job_id)
    if job is None:
        raise PipelineJobNotFoundError(job_id)
    reconcile_stale_pipeline_job(session, job)
    state = repo.load_state(job)
    return map_pipeline_run_response(state)


def get_latest_pipeline_job_detail(
    session: Session,
    project_id: str,
) -> VideoPipelineJobDetailResponse:
    """查询项目最近 Job 详情。"""
    repo = VideoPipelineJobRepository(session)
    job = repo.get_latest_job_for_project(project_id)
    if job is None:
        raise PipelineJobNotFoundError(project_id)
    reconcile_stale_pipeline_job(session, job)
    run_view = map_pipeline_run_response(repo.load_state(job))
    return VideoPipelineJobDetailResponse(
        job_id=job.job_id,
        project_id=job.project_id,
        status=job.status,
        run=run_view,
    )


def _resolve_job_status(state: VideoPipelineState) -> str:
    """将 state 映射为 Job 表 status。"""
    if state.run_status == PIPELINE_RUN_COMPLETED and not state.paused:
        return PIPELINE_JOB_STATUS_COMPLETED
    if state.paused or state.run_status == PIPELINE_RUN_PAUSED:
        return PIPELINE_JOB_STATUS_PAUSED
    if state.error_message:
        return PIPELINE_JOB_STATUS_FAILED
    return PIPELINE_JOB_STATUS_RUNNING
