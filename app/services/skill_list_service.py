"""Skill 列表服务辅助。

【职责】
    组装 GET /skills 的响应（复用 discover_skills，不含 system_prompt 全文）。
"""

from app.schemas.skill_list import SkillListItem, SkillListResponse
from app.skills.registry import discover_skills
from app.skills.skill_models import SkillDefinition


def build_skill_list_response() -> SkillListResponse:
    """扫描 skills/ 目录并返回列表响应。

    返回:
        SkillListResponse: 全部已注册 Skill 的元数据。
    """
    definitions = discover_skills()
    items = [_to_item(defn) for defn in definitions]
    return SkillListResponse(items=items)


def _to_item(defn: SkillDefinition) -> SkillListItem:
    """SkillDefinition 转 API 列表项。"""
    return SkillListItem(
        id=defn.skill_id,
        display_name=defn.display_name,
        description=defn.description,
        triggers=defn.triggers,
    )
