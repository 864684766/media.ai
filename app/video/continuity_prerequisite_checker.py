"""连续性 QA：渲染前置条件规则。"""

from app.core.video_constants import REASON_INVALID_DURATION, REASON_MISSING_KEYFRAME
from app.models.postgres.shot_model import ShotModel


def collect_prerequisite_reasons(shot: ShotModel) -> list[str]:
    """检查 rendered 镜头是否具备 QA 所需字段。

    参数:
        shot: 待检镜头。

    返回:
        list[str]: 失败原因；空则通过。
    """
    reasons: list[str] = []
    reasons.extend(_check_keyframe(shot))
    reasons.extend(_check_duration(shot))
    return reasons


def _check_keyframe(shot: ShotModel) -> list[str]:
    """关键帧 URI 必须已写入。"""
    if not (shot.keyframe_uri or "").strip():
        return [REASON_MISSING_KEYFRAME]
    return []


def _check_duration(shot: ShotModel) -> list[str]:
    """时长必须为正。"""
    if shot.duration_sec <= 0:
        return [REASON_INVALID_DURATION]
    return []
