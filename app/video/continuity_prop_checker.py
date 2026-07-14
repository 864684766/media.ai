"""连续性 QA：同场景道具不得无故消失。"""

from app.core.video_constants import REASON_PROP_DROPPED
from app.models.postgres.shot_model import ShotModel


def collect_prop_continuity_reasons(
    shot: ShotModel,
    previous_shot: ShotModel | None,
) -> list[str]:
    """同场景下上一镜道具不得无故丢失。

    参数:
        shot: 当前镜。
        previous_shot: 上一镜。

    返回:
        list[str]: 失败原因；空则通过。
    """
    if previous_shot is None:
        return []
    return _dropped_props_in_same_scene(shot, previous_shot)


def _dropped_props_in_same_scene(
    shot: ShotModel,
    previous_shot: ShotModel,
) -> list[str]:
    """同场景比较道具集合。"""
    if (previous_shot.scene_id or "") != (shot.scene_id or ""):
        return []
    prev_props = set(previous_shot.prop_ids or [])
    curr_props = set(shot.prop_ids or [])
    rows: list[str] = []
    for prop_id in prev_props:
        if prop_id and prop_id not in curr_props:
            rows.append(f"{REASON_PROP_DROPPED}: {prop_id}")
    return rows
