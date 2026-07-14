"""HITL 镜头审核业务服务。"""

from sqlalchemy.orm import Session

from app.core.video_constants import REVIEW_STAGE_QA_OVERFLOW
from app.schemas.video_review import ShotReviewRequest, ShotReviewResponse
from app.storage.postgres.shot_repository import ShotRepository
from app.video.shot_review_transition_resolver import resolve_review_target_status
from app.video.shot_row_mapper import shot_model_to_output


class ShotReviewError(Exception):
    """非法审核请求。"""

    def __init__(self, message: str) -> None:
        """保存错误说明。"""
        self.message = message
        super().__init__(message)


def review_shot(
    session: Session,
    shot_id: str,
    body: ShotReviewRequest,
) -> ShotReviewResponse:
    """执行 HITL 审核并写回状态。"""
    repo = ShotRepository(session)
    shot = repo.get_shot(shot_id)
    if shot is None:
        raise ShotReviewError("镜头不存在")
    previous = shot.status
    target = resolve_review_target_status(previous, body.stage, body.action)
    if target is None:
        raise ShotReviewError("当前状态不允许该审核操作")
    repo.update_shot_status(shot_id, target)
    _reset_qa_on_approve(repo, body, target, shot_id)
    refreshed = repo.get_shot(shot_id)
    assert refreshed is not None
    return ShotReviewResponse(
        shot=shot_model_to_output(refreshed),
        previous_status=previous,
        comment=body.comment,
    )


def _reset_qa_on_approve(repo, body, target, shot_id: str) -> None:
    """QA 人工通过时清零重试计数。"""
    from app.core.video_constants import REVIEW_ACTION_APPROVE, SHOT_STATUS_QA_PASSED

    if body.stage != REVIEW_STAGE_QA_OVERFLOW:
        return
    if body.action != REVIEW_ACTION_APPROVE:
        return
    if target != SHOT_STATUS_QA_PASSED:
        return
    repo.reset_qa_attempts(shot_id)
