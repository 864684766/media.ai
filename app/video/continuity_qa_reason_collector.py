"""连续性 QA 原因汇总（纯逻辑）。"""

from app.models.postgres.shot_model import ShotModel
from app.video.continuity_prerequisite_checker import collect_prerequisite_reasons
from app.video.continuity_prop_checker import collect_prop_continuity_reasons
from app.video.continuity_transition_checker import collect_transition_reasons
from app.video.entity_validation_checker import BibleIdSets, collect_shot_validation_reasons


def collect_continuity_qa_reasons(
    shot: ShotModel,
    previous_shot: ShotModel | None,
    bible_ids: BibleIdSets,
) -> list[str]:
    """汇总单镜连续性 QA 失败原因。

    参数:
        shot: 当前镜（status=rendered）。
        previous_shot: 按镜号排序的上一镜。
        bible_ids: bible ID 集合。

    返回:
        list[str]: 空列表表示通过。
    """
    reasons: list[str] = []
    reasons.extend(collect_prerequisite_reasons(shot))
    reasons.extend(collect_shot_validation_reasons(shot, bible_ids))
    reasons.extend(collect_transition_reasons(shot, previous_shot))
    reasons.extend(collect_prop_continuity_reasons(shot, previous_shot))
    return reasons
