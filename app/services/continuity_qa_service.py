"""连续性 QA 业务服务（V4 规则版）。"""

from sqlalchemy.orm import Session

from app.core.video_constants import (
    SHOT_STATUS_AWAITING_REVIEW,
    SHOT_STATUS_QA_FAILED,
    SHOT_STATUS_QA_PASSED,
)
from app.schemas.video_qa import ContinuityQaResponse, ShotQaFailure
from app.services.entity_validation_service import load_bible_id_sets
from app.storage.postgres.shot_repository import ShotRepository
from app.video.continuity_qa_reason_collector import collect_continuity_qa_reasons
from app.video.video_qa_config_reader import load_video_qa_config


def run_continuity_qa(session: Session, project_id: str) -> ContinuityQaResponse:
    """对 rendered 镜头执行规则 QA 并迁移状态。"""
    config = load_video_qa_config()
    shot_repo = ShotRepository(session)
    bible_ids = load_bible_id_sets(session, project_id)
    shots = shot_repo.list_rendered_by_project(project_id)
    return _apply_qa_to_shots(shot_repo, shots, bible_ids, project_id, config.max_retries)


def _apply_qa_to_shots(
    shot_repo: ShotRepository,
    shots: list,
    bible_ids,
    project_id: str,
    max_retries: int,
) -> ContinuityQaResponse:
    """逐镜 QA 并统计结果。"""
    passed = 0
    failed = 0
    awaiting = 0
    failures: list[ShotQaFailure] = []
    previous = None
    for shot in shots:
        outcome = _qa_one_shot(shot_repo, shot, previous, bible_ids, max_retries)
        passed += outcome["passed"]
        failed += outcome["failed"]
        awaiting += outcome["awaiting"]
        if outcome["failure"]:
            failures.append(outcome["failure"])
        previous = shot
    return ContinuityQaResponse(
        project_id=project_id,
        passed_count=passed,
        failed_count=failed,
        awaiting_review_count=awaiting,
        failures=failures,
    )


def _qa_one_shot(shot_repo, shot, previous, bible_ids, max_retries: int) -> dict:
    """QA 单镜并写回状态。"""
    reasons = collect_continuity_qa_reasons(shot, previous, bible_ids)
    if not reasons:
        shot_repo.update_shot_status(shot.shot_id, SHOT_STATUS_QA_PASSED)
        return {"passed": 1, "failed": 0, "awaiting": 0, "failure": None}
    attempts = shot_repo.increment_qa_attempts(shot.shot_id)
    if attempts >= max_retries:
        shot_repo.update_shot_status(shot.shot_id, SHOT_STATUS_AWAITING_REVIEW)
        status = SHOT_STATUS_AWAITING_REVIEW
        bucket = {"passed": 0, "failed": 0, "awaiting": 1}
    else:
        shot_repo.update_shot_status(shot.shot_id, SHOT_STATUS_QA_FAILED)
        status = SHOT_STATUS_QA_FAILED
        bucket = {"passed": 0, "failed": 1, "awaiting": 0}
    failure = ShotQaFailure(
        shot_id=shot.shot_id,
        shot_no=shot.shot_no,
        status=status,
        reasons=reasons,
    )
    return {**bucket, "failure": failure}
