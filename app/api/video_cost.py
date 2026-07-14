"""视频项目成本 API（V7）。"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_cost import ProjectCostOutput
from app.services.video_cost_service import get_project_cost
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 PG 时 503。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")


@router.get(
    "/projects/{project_id}/cost",
    summary="查询项目成本与预算",
    response_model=ProjectCostOutput,
)
def get_video_project_cost(project_id: str) -> ProjectCostOutput:
    """汇总 shot_assets.cost 与 budget 状态。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return get_project_cost(session, project_id)
