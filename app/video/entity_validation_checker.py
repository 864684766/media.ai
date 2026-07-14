"""单镜实体引用校验（纯逻辑，无 DB）。

【职责】
    检查镜头引用的 character/scene/prop ID 是否存在于 bible 集合。
"""

from dataclasses import dataclass

from app.core.video_constants import (
    REASON_MISSING_CHARACTER,
    REASON_MISSING_PROP,
    REASON_MISSING_SCENE,
)
from app.models.postgres.shot_model import ShotModel


@dataclass(frozen=True)
class BibleIdSets:
    """project 下 bible ID 集合。

    字段:
        character_ids: 已登记角色 ID。
        scene_ids: 已登记场景 ID。
        prop_ids: 已登记道具 ID。
    """

    character_ids: set[str]
    scene_ids: set[str]
    prop_ids: set[str]


def collect_shot_validation_reasons(
    shot: ShotModel,
    bible_ids: BibleIdSets,
) -> list[str]:
    """收集单镜校验失败原因（空列表表示通过）。

    参数:
        shot: 待校验镜头。
        bible_ids: bible ID 集合。

    返回:
        list[str]: 失败原因；空则通过。
    """
    reasons: list[str] = []
    reasons.extend(_missing_characters(shot, bible_ids.character_ids))
    reasons.extend(_missing_scene(shot, bible_ids.scene_ids))
    reasons.extend(_missing_props(shot, bible_ids.prop_ids))
    return reasons


def _missing_characters(shot: ShotModel, known: set[str]) -> list[str]:
    """检查角色 ID 是否齐全。"""
    rows: list[str] = []
    for cid in shot.character_ids or []:
        if cid and cid not in known:
            rows.append(f"{REASON_MISSING_CHARACTER}: {cid}")
    return rows


def _missing_scene(shot: ShotModel, known: set[str]) -> list[str]:
    """检查场景 ID 是否存在。"""
    scene_id = (shot.scene_id or "").strip()
    if scene_id and scene_id not in known:
        return [f"{REASON_MISSING_SCENE}: {scene_id}"]
    return []


def _missing_props(shot: ShotModel, known: set[str]) -> list[str]:
    """检查道具 ID 是否齐全。"""
    rows: list[str] = []
    for pid in shot.prop_ids or []:
        if pid and pid not in known:
            rows.append(f"{REASON_MISSING_PROP}: {pid}")
    return rows
