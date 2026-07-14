"""Skill 匹配逻辑。

【本文件职责】
    在多个 Skill 中选出「本轮该用哪一个」。

【优先级】（高 → 低）
    1. 客户端显式 skill_id=video-editing
    2. 用户消息包含某 Skill 的 triggers（如「续写」→ novel-writing）
    3. discover 列表里的第一个（兜底）

【为何放在独立文件】
    以后若改为 LLM 分类匹配，只改本文件，不动 registry 扫描逻辑。
"""

from app.skills.skill_models import SkillDefinition


def match_skill_definition(
    skills: list[SkillDefinition],
    skill_id: str | None,
    user_message: str,
) -> SkillDefinition | None:
    """从已发现 Skill 列表中选出最合适的一项。

    参数:
        skills: discover_skills 返回的列表。
        skill_id: 客户端显式指定的 skill_id，优先级最高。
        user_message: 用户本轮输入，用于 triggers 匹配。

    返回:
        SkillDefinition | None: 匹配结果；列表为空时返回 None。
    """
    if not skills:
        return None
    by_id = _match_by_skill_id(skills, skill_id)
    if by_id is not None:
        return by_id
    by_trigger = _match_by_triggers(skills, user_message)
    if by_trigger is not None:
        return by_trigger
    return skills[0]


def _match_by_skill_id(
    skills: list[SkillDefinition],
    skill_id: str | None,
) -> SkillDefinition | None:
    """按 skill_id 精确查找。"""
    if not skill_id or not skill_id.strip():
        return None
    target = skill_id.strip()
    for item in skills:
        if item.skill_id == target:
            return item
    return None


def _match_by_triggers(
    skills: list[SkillDefinition],
    user_message: str,
) -> SkillDefinition | None:
    """用户消息包含 trigger 词时命中对应 Skill。"""
    message = user_message.strip()
    if not message:
        return None
    for item in skills:
        if _message_hits_triggers(message, item.triggers):
            return item
    return None


def _message_hits_triggers(message: str, triggers: list[str]) -> bool:
    """判断消息是否包含任一 trigger（子串匹配，区分大小写由中文主导）。"""
    for trigger in triggers:
        if trigger and trigger in message:
            return True
    return False
