"""pipeline_blocking_reason_resolver 单元测试。"""

from app.core.video_constants import SHOT_STATUS_REJECTED, SHOT_STATUS_VALIDATED
from app.core.video_pipeline_run_constants import PAUSE_REASON_ALL_SHOTS_REJECTED
from app.video.pipeline_blocking_reason_resolver import resolve_pipeline_blocking_reason


def test_no_blocking_when_all_validated() -> None:
    """全部 validated 时不应阻断。"""
    reason = resolve_pipeline_blocking_reason(
        5,
        {SHOT_STATUS_VALIDATED: 5},
    )
    assert reason == ""


def test_all_rejected_blocks() -> None:
    """全部 rejected 时应阻断。"""
    reason = resolve_pipeline_blocking_reason(
        3,
        {SHOT_STATUS_REJECTED: 3},
    )
    assert reason == PAUSE_REASON_ALL_SHOTS_REJECTED
