"""镜头渲染成本计算（V7）。

【职责】
    按 duration_sec × cost_per_second 估算单镜 clip 费用。

【何时调用】
    render Job 记账与 budget 预估。
"""

from app.models.postgres.shot_model import ShotModel
from app.video.provider_capability_model import ProviderCapability


def calculate_shot_clip_cost(shot: ShotModel, capability: ProviderCapability) -> float:
    """计算单镜 clip 成本。

    参数:
        shot: 镜头 ORM（含 duration_sec）。
        capability: Provider 能力（含 cost_per_second）。

    返回:
        float: 美元占位成本。
    """
    seconds = float(shot.duration_sec or 0)
    return round(seconds * capability.cost_per_second, 6)


def calculate_shots_clip_cost(
    shots: list[ShotModel],
    capability: ProviderCapability,
) -> float:
    """批量估算 clip 总成本。"""
    total = sum(calculate_shot_clip_cost(shot, capability) for shot in shots)
    return round(total, 6)
