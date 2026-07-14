"""视频流水线状态 API（V6 + D1/D3）。"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.core.video_pipeline_job_constants import PIPELINE_JOB_STATUS_PENDING
from app.schemas.video_pipeline import PipelineStatusResponse
from app.schemas.video_pipeline_job import (
    VideoPipelineJobDetailResponse,
    VideoPipelineJobStartResponse,
)
from app.schemas.video_pipeline_run import VideoPipelineRunResponse
from app.services.video_pipeline_async_service import (
    PipelineJobNotFoundError,
    get_pipeline_job_status,
    get_latest_pipeline_job_detail,
    resume_pipeline_job,
    start_async_pipeline_job,
)
from app.services.video_pipeline_run_service import run_video_pipeline
from app.services.video_pipeline_status_service import get_pipeline_status
from app.services.video_pipeline_worker_thread import spawn_pipeline_worker
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured
from app.storage.postgres.video_pipeline_job_repository import VideoPipelineJobRepository

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 PG 时 503。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")


@router.get(
    "/projects/{project_id}/pipeline",
    summary="流水线进度与待审镜头",
    response_model=PipelineStatusResponse,
)
def get_project_pipeline(project_id: str) -> PipelineStatusResponse:
    """返回各状态计数、步骤进度、awaiting_review 列表。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return get_pipeline_status(session, project_id)


@router.post(
    "/projects/{project_id}/pipeline/run",
    summary="LangGraph 一键跑视频管线",
    response_model=VideoPipelineRunResponse,
)
def post_run_project_pipeline(project_id: str) -> VideoPipelineRunResponse:
    """按子图顺序执行 validate→render→qa→audio→compose；HITL 时 paused。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return run_video_pipeline(session, project_id)


@router.post(
    "/projects/{project_id}/pipeline/run/async",
    summary="异步启动视频管线 Job",
    response_model=VideoPipelineJobStartResponse,
)
def post_run_project_pipeline_async(project_id: str) -> VideoPipelineJobStartResponse:
    """创建 Job 并后台执行；断点写入 video_pipeline_jobs。"""
    _require_postgres()
    with postgres_session_scope() as session:
        job_id = start_async_pipeline_job(session, project_id)
    spawn_pipeline_worker(job_id)
    return VideoPipelineJobStartResponse(
        job_id=job_id,
        project_id=project_id,
        status=PIPELINE_JOB_STATUS_PENDING,
    )


@router.get(
    "/projects/{project_id}/pipeline/jobs/latest",
    summary="查询项目最近管线 Job",
    response_model=VideoPipelineJobDetailResponse,
)
def get_latest_project_pipeline_job(project_id: str) -> VideoPipelineJobDetailResponse:
    """返回 project 最近一条 Job；不存在时 404。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            return get_latest_pipeline_job_detail(session, project_id)
    except PipelineJobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Job 不存在: {exc.job_id}") from exc


@router.get(
    "/pipeline/jobs/{job_id}",
    summary="查询管线 Job checkpoint",
    response_model=VideoPipelineJobDetailResponse,
)
def get_pipeline_job(job_id: str) -> VideoPipelineJobDetailResponse:
    """返回 Job 状态与 checkpoint 映射的运行结果。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            run_view = get_pipeline_job_status(session, job_id)
            job = VideoPipelineJobRepository(session).get_job(job_id)
            assert job is not None
            return VideoPipelineJobDetailResponse(
                job_id=job_id,
                project_id=job.project_id,
                status=job.status,
                run=run_view,
            )
    except PipelineJobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Job 不存在: {exc.job_id}") from exc


@router.post(
    "/pipeline/jobs/{job_id}/resume",
    summary="断点续跑管线 Job",
    response_model=VideoPipelineJobDetailResponse,
)
def post_resume_pipeline_job(job_id: str) -> VideoPipelineJobDetailResponse:
    """从 steps_completed 后续步骤继续执行。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            run_view = resume_pipeline_job(session, job_id)
            job = VideoPipelineJobRepository(session).get_job(job_id)
            assert job is not None
            return VideoPipelineJobDetailResponse(
                job_id=job_id,
                project_id=job.project_id,
                status=job.status,
                run=run_view,
            )
    except PipelineJobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Job 不存在: {exc.job_id}") from exc
