"""HITL 审核状态迁移（纯逻辑）。"""

from app.core.video_constants import (
    REVIEW_ACTION_APPROVE,
    REVIEW_ACTION_REJECT,
    REVIEW_STAGE_KEYFRAME,
    REVIEW_STAGE_QA_OVERFLOW,
    REVIEW_STAGE_STORYBOARD,
    SHOT_STATUS_AWAITING_REVIEW,
    SHOT_STATUS_DRAFT,
    SHOT_STATUS_QA_PASSED,
    SHOT_STATUS_REJECTED,
    SHOT_STATUS_RENDERED,
    SHOT_STATUS_VALIDATED,
)


def resolve_review_target_status(
    current_status: str,
    stage: str,
    action: str,
) -> str | None:
    """根据阶段与动作解析目标状态。

    参数:
        current_status: 镜头当前状态。
        stage: HITL 阶段。
        action: approve / reject。

    返回:
        str | None: 新状态；None 表示非法组合。
    """
    if stage == REVIEW_STAGE_QA_OVERFLOW:
        return _qa_overflow_transition(current_status, action)
    if stage == REVIEW_STAGE_KEYFRAME:
        return _keyframe_transition(current_status, action)
    if stage == REVIEW_STAGE_STORYBOARD:
        return _storyboard_transition(current_status, action)
    return None


def _qa_overflow_transition(current_status: str, action: str) -> str | None:
    """QA 超限人工审核。"""
    if current_status != SHOT_STATUS_AWAITING_REVIEW:
        return None
    if action == REVIEW_ACTION_APPROVE:
        return SHOT_STATUS_QA_PASSED
    if action == REVIEW_ACTION_REJECT:
        return SHOT_STATUS_REJECTED
    return None


def _keyframe_transition(current_status: str, action: str) -> str | None:
    """关键帧确认（rendered 阶段）。"""
    if current_status != SHOT_STATUS_RENDERED:
        return None
    if action == REVIEW_ACTION_APPROVE:
        return SHOT_STATUS_RENDERED
    if action == REVIEW_ACTION_REJECT:
        return SHOT_STATUS_VALIDATED
    return None


def _storyboard_transition(current_status: str, action: str) -> str | None:
    """分镜确认（draft 阶段，通过后保持 draft 待 validate）。"""
    if current_status != SHOT_STATUS_DRAFT:
        return None
    if action == REVIEW_ACTION_APPROVE:
        return SHOT_STATUS_DRAFT
    if action == REVIEW_ACTION_REJECT:
        return SHOT_STATUS_REJECTED
    return None
