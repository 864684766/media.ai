"""流水线状态聚合（纯逻辑）。"""

from collections import Counter

from app.models.postgres.shot_model import ShotModel


def aggregate_status_counts(shots: list[ShotModel]) -> dict[str, int]:
    """按 status 统计镜头数量。

    参数:
        shots: project 下全部镜头。

    返回:
        dict[str, int]: status → count。
    """
    counter = Counter(shot.status for shot in shots)
    return dict(counter)
