"""连续性 QA：相邻镜场景跳变规则。"""

from app.core.video_constants import REASON_MISSING_TRANSITION
from app.models.postgres.shot_model import ShotModel


def collect_transition_reasons(
    shot: ShotModel,
    previous_shot: ShotModel | None,
) -> list[str]:
    """相邻镜 scene_id 变更时须标注 transition。

    参数:
        shot: 当前镜。
        previous_shot: 上一镜（按镜号排序）。

    返回:
        list[str]: 失败原因；空则通过。
    """
    if previous_shot is None:
        return []
    return _scene_jump_without_transition(shot, previous_shot)


def _scene_jump_without_transition(
    shot: ShotModel,
    previous_shot: ShotModel,
) -> list[str]:
    """场景变更但 transition 为空则失败。"""
    prev_scene = (previous_shot.scene_id or "").strip()
    curr_scene = (shot.scene_id or "").strip()
    if not prev_scene or not curr_scene or prev_scene == curr_scene:
        return []
    if (shot.transition or "").strip():
        return []
    return [f"{REASON_MISSING_TRANSITION}: {prev_scene} -> {curr_scene}"]
