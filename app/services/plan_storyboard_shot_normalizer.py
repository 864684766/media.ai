"""分镜 dict 列表规范为 ShotInput。"""

from app.schemas.video_shot import ShotInput

DEFAULT_MIN_DURATION_SEC = 1.0
DEFAULT_SHOT_NO = "1"


def normalize_storyboard_shots(rows: list[dict]) -> list[ShotInput]:
    """将解析后的 dict 列表转为 ShotInput。

    参数:
        rows: parse_storyboard_json_array 产出。

    返回:
        list[ShotInput]: 可供 submit_storyboard 入库的列表。
    """
    return [_dict_to_shot_input(row, index) for index, row in enumerate(rows)]


def _dict_to_shot_input(row: dict, index: int) -> ShotInput:
    """单条 dict → ShotInput，补全缺省字段。"""
    duration = _positive_duration(row.get("duration_sec"))
    shot_no = str(row.get("shot_no") or index + 1)
    return ShotInput(
        shot_no=shot_no or DEFAULT_SHOT_NO,
        duration_sec=duration,
        shot_size=str(row.get("shot_size", "")),
        camera=str(row.get("camera", "")),
        action=str(row.get("action", "")),
        dialogue=str(row.get("dialogue", "")),
        sfx=str(row.get("sfx", "")),
        character_ids=list(row.get("character_ids") or []),
        scene_id=str(row.get("scene_id", "")),
        prop_ids=list(row.get("prop_ids") or []),
        transition=str(row.get("transition", "")),
    )


def _positive_duration(raw: object) -> float:
    """保证时长为正数。"""
    try:
        value = float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return DEFAULT_MIN_DURATION_SEC
    if value <= 0:
        return DEFAULT_MIN_DURATION_SEC
    return value
