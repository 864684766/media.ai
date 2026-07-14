"""从单镜字段移除 Bible 实体引用（纯逻辑）。"""

from app.models.postgres.shot_model import ShotModel


def apply_bible_ref_strip(
    shot: ShotModel,
    character_ids: set[str],
    scene_ids: set[str],
    prop_ids: set[str],
) -> bool:
    """从镜头 JSON 字段剔除指定 ID。

    参数:
        shot: 待修改镜头。
        character_ids: 要移除的角色 ID。
        scene_ids: 要清空的场景 ID。
        prop_ids: 要移除的道具 ID。

    返回:
        bool: 是否发生变更。
    """
    changed = False
    changed = _strip_characters(shot, character_ids) or changed
    changed = _strip_scene(shot, scene_ids) or changed
    changed = _strip_props(shot, prop_ids) or changed
    return changed


def _strip_characters(shot: ShotModel, remove_ids: set[str]) -> bool:
    """过滤 character_ids。"""
    if not remove_ids:
        return False
    current = list(shot.character_ids or [])
    filtered = [cid for cid in current if cid not in remove_ids]
    if filtered == current:
        return False
    shot.character_ids = filtered
    return True


def _strip_scene(shot: ShotModel, remove_ids: set[str]) -> bool:
    """清空匹配的 scene_id。"""
    scene_id = (shot.scene_id or "").strip()
    if not scene_id or scene_id not in remove_ids:
        return False
    shot.scene_id = ""
    return True


def _strip_props(shot: ShotModel, remove_ids: set[str]) -> bool:
    """过滤 prop_ids。"""
    if not remove_ids:
        return False
    current = list(shot.prop_ids or [])
    filtered = [pid for pid in current if pid not in remove_ids]
    if filtered == current:
        return False
    shot.prop_ids = filtered
    return True
