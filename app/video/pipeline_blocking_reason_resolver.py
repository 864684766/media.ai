"""流水线阻断原因解析（供 GET pipeline 展示）。"""

from app.core.video_constants import SHOT_STATUS_REJECTED, SHOT_STATUS_VALIDATED
from app.core.video_pipeline_run_constants import (
    PAUSE_REASON_ALL_SHOTS_REJECTED,
    PAUSE_REASON_NO_SHOTS,
    PAUSE_REASON_NO_VALIDATED_SHOTS,
)


def resolve_pipeline_blocking_reason(
    shots_total: int,
    status_counts: dict[str, int],
) -> str:
    """根据镜头状态汇总阻断码。

    参数:
        shots_total: 镜头总数。
        status_counts: status → 数量。

    返回:
        str: 空字符串表示无阻断；否则为原因码。
    """
    if shots_total <= 0:
        return PAUSE_REASON_NO_SHOTS
    rejected = status_counts.get(SHOT_STATUS_REJECTED, 0)
    if rejected >= shots_total:
        return PAUSE_REASON_ALL_SHOTS_REJECTED
    validated = status_counts.get(SHOT_STATUS_VALIDATED, 0)
    rendered = _count_rendered_or_beyond(status_counts)
    if validated <= 0 and rendered <= 0 and rejected > 0:
        return PAUSE_REASON_NO_VALIDATED_SHOTS
    return ""


def _count_rendered_or_beyond(status_counts: dict[str, int]) -> int:
    """统计已进入渲染及之后阶段的镜头数。"""
    keys = ("rendered", "rendering", "qa_passed", "qa_failed", "awaiting_review", "composed")
    return sum(status_counts.get(key, 0) for key in keys)
