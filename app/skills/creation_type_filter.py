"""按创作类型过滤 Skill 列表。

【职责】
    根据 ChatRequest.creation_type 缩小 Skill 候选池，
    使小说/视频走不同的人设与生成链路（sec-10.4）。
"""

from app.core.creation_type_constants import (
    CREATION_TYPE_NOVEL,
    CREATION_TYPE_VIDEO,
    NOVEL_SKILL_IDS,
    VIDEO_SKILL_IDS,
    VIDEO_SKILL_PRIORITY,
)
from app.skills.skill_models import SkillDefinition


def filter_skills_by_creation_type(
    skills: list[SkillDefinition],
    creation_type: str | None,
) -> list[SkillDefinition]:
    """按创作类型过滤 Skill 列表。

    参数:
        skills: discover_skills 全量列表。
        creation_type: novel / video；None 表示不过滤。

    返回:
        list[SkillDefinition]: 过滤并排序后的候选池。
    """
    if not creation_type:
        return skills
    allowed = _allowed_ids_for_type(creation_type)
    filtered = [item for item in skills if item.skill_id in allowed]
    return _sort_by_priority(filtered, creation_type)


def _allowed_ids_for_type(creation_type: str) -> frozenset[str]:
    """返回某创作类型允许的 skill_id 集合。"""
    if creation_type == CREATION_TYPE_VIDEO:
        return VIDEO_SKILL_IDS
    return NOVEL_SKILL_IDS


def _sort_by_priority(
    skills: list[SkillDefinition],
    creation_type: str,
) -> list[SkillDefinition]:
    """视频类按导演优先排序，小说类保持原序。"""
    if creation_type != CREATION_TYPE_VIDEO:
        return skills
    order = {skill_id: index for index, skill_id in enumerate(VIDEO_SKILL_PRIORITY)}
    return sorted(skills, key=lambda item: order.get(item.skill_id, 99))
