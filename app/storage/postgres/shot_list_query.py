"""Shot 列表查询辅助（按镜号自然排序）。

【职责】
    将 project 下全部镜头读出后按 shot_no 排序，Repository 不膨胀。
"""

from app.models.postgres.shot_model import ShotModel


def _shot_no_sort_key(shot_no: str) -> tuple[int, str]:
    """生成镜号排序键（数字优先，其次原字符串）。

    参数:
        shot_no: 镜号字符串。

    返回:
        tuple: (数字部分, 原串) 供 sorted 使用。
    """
    digits = "".join(ch for ch in shot_no if ch.isdigit())
    number = int(digits) if digits else 0
    return (number, shot_no)


def sort_shots_by_shot_no(rows: list[ShotModel]) -> list[ShotModel]:
    """按镜号升序排列镜头列表。

    参数:
        rows: 未排序的 ShotModel 列表。

    返回:
        list[ShotModel]: 排序后的新列表（不修改入参顺序对象）。
    """
    return sorted(rows, key=lambda row: _shot_no_sort_key(row.shot_no))
