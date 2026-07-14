"""HITL 镜头审核 API（V6）。"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_review import ShotReviewRequest, ShotReviewResponse
from app.services.shot_review_service import ShotReviewError, review_shot
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 PG 时 503。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")


@router.post(
    "/shots/{shot_id}/review",
    summary="HITL 审核镜头",
    response_model=ShotReviewResponse,
)
def post_shot_review(shot_id: str, body: ShotReviewRequest) -> ShotReviewResponse:
    """approve/reject：qa_overflow、keyframe、storyboard 阶段。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            return review_shot(session, shot_id, body)
    except ShotReviewError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
