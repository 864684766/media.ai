"""判定管线 Job checkpoint 是否已被镜头现状否定。"""

from app.core.video_pipeline_run_constants import (
    PAUSE_REASON_ALL_SHOTS_REJECTED,
    PAUSE_REASON_NO_VALIDATED_SHOTS,
)
from app.schemas.video_pipeline_state import VideoPipelineState
from app.video.pipeline_blocking_reason_resolver import resolve_pipeline_blocking_reason

# 与 Style Bible / 实体校验相关的暂停码
BIBLE_ENTITY_PAUSE_REASONS = frozenset(
    {
        PAUSE_REASON_NO_VALIDATED_SHOTS,
        PAUSE_REASON_ALL_SHOTS_REJECTED,
    },
)


def is_stale_bible_entity_pause(
    state: VideoPipelineState,
    status_counts: dict[str, int],
    shots_total: int,
) -> bool:
    """Bible 类暂停是否已过时（镜头已校验通过且 pipeline 无阻断）。

    参数:
        state: Job checkpoint。
        status_counts: 镜头 status 计数。
        shots_total: 镜头总数。

    返回:
        bool: True 表示应 reconcile 为 completed。
    """
    if not _is_bible_entity_pause(state):
        return False
    if resolve_pipeline_blocking_reason(shots_total, status_counts):
        return False
    return _count_validated_or_beyond(status_counts) > 0


def _is_bible_entity_pause(state: VideoPipelineState) -> bool:
    """是否为 Bible 实体校验类暂停。"""
    if state.pause_reason in BIBLE_ENTITY_PAUSE_REASONS:
        return True
    return state.paused and state.current_step == "validate_entities"


def _count_validated_or_beyond(status_counts: dict[str, int]) -> int:
    """统计 validated 及之后阶段的镜头数。"""
    keys = ("validated", "rendered", "rendering", "qa_passed", "qa_failed", "composed")
    return sum(status_counts.get(key, 0) for key in keys)
