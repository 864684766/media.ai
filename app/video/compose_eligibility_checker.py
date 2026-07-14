"""合成资格检查（纯逻辑）。"""

from app.core.video_constants import REASON_NO_QA_PASSED_SHOTS
from app.models.postgres.shot_model import ShotModel


def collect_compose_block_reasons(shots: list[ShotModel]) -> list[str]:
    """检查是否具备合成条件。

    参数:
        shots: qa_passed 镜头列表。

    返回:
        list[str]: 空列表表示可合成。
    """
    if not shots:
        return [REASON_NO_QA_PASSED_SHOTS]
    return []
