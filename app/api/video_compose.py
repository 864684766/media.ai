"""视频时间轴合成 API（V5）。"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_compose import ComposeJobOutput, ComposeStartResponse
from app.services.compose_job_service import ComposeBlockedError, get_compose_job, start_compose_job
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
    "/projects/{project_id}/compose",
    summary="启动时间轴合成",
    response_model=ComposeStartResponse,
)
def post_start_compose(project_id: str) -> ComposeStartResponse:
    """仅纳入 qa_passed 镜头，写出 timeline JSON 或 mp4。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            return start_compose_job(session, project_id)
    except ComposeBlockedError as exc:
        raise HTTPException(status_code=400, detail=exc.reasons) from exc
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
    "/compose/jobs/{job_id}",
    summary="查询合成 Job",
    response_model=ComposeJobOutput,
)
def get_compose_job_status(job_id: str) -> ComposeJobOutput:
    """返回合成 Job 与产物 URI。"""
    _require_postgres()
    with postgres_session_scope() as session:
        job = get_compose_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job 不存在")
    return job
