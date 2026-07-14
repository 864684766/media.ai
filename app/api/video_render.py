"""视频渲染与 Job 查询 API（V3）。"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_render import RenderJobOutput, RenderStartResponse
from app.services.render_job_service import get_render_job, start_render_job
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured
from app.video.ffmpeg_required_checker import FfmpegRequiredError
from app.video.project_budget_gate import BudgetExceededError
from app.video.video_budget_constants import REASON_BUDGET_EXCEEDED

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 PG 时 503。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")


@router.post(
    "/projects/{project_id}/render",
    summary="启动渲染 Job",
    response_model=RenderStartResponse,
)
def post_start_render(project_id: str) -> RenderStartResponse:
    """对 validated 镜头写出关键帧/切片（Provider 可配置）。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            return start_render_job(session, project_id)
    except BudgetExceededError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "reason": REASON_BUDGET_EXCEEDED,
                "project_id": exc.project_id,
                "total_cost_usd": exc.total_cost_usd,
                "budget_limit_usd": exc.budget_limit_usd,
            },
        ) from exc
    except FfmpegRequiredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get(
    "/jobs/{job_id}",
    summary="查询渲染 Job",
    response_model=RenderJobOutput,
)
def get_job_status(job_id: str) -> RenderJobOutput:
    """返回 Job 进度。"""
    _require_postgres()
    with postgres_session_scope() as session:
        job = get_render_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job 不存在")
    return job
