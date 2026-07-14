"""视频连续性 QA API（V4）。"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_qa import ContinuityQaResponse
from app.services.continuity_qa_service import run_continuity_qa
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 PG 时 503。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")


@router.post(
    "/projects/{project_id}/qa",
    summary="连续性 QA（规则版）",
    response_model=ContinuityQaResponse,
)
def post_continuity_qa(project_id: str) -> ContinuityQaResponse:
    """扫描 rendered 镜头 → qa_passed / qa_failed / awaiting_review。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return run_continuity_qa(session, project_id)
