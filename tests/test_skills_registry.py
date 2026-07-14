"""Skill Registry 示例测试。

验证 app/skills/ 代码能扫描根目录 skills/ 并加载 system prompt。
"""

from app.skills import discover_skills, load_skill_context


def test_discover_skills_includes_novel_writing() -> None:
    """扫描应发现 skills/novel-writing/SKILL.md。"""
    skills = discover_skills()
    skill_ids = [item.skill_id for item in skills]
    assert "novel-writing" in skill_ids


def test_load_skill_context_by_skill_id() -> None:
    """指定 skill_id 应加载 prompts/system.md 到 system_prompt。"""
    context = load_skill_context(skill_id="novel-writing")
    assert context.id == "novel-writing"
    assert "资深玄幻小说作家" in context.system_prompt


def test_load_skill_context_by_trigger() -> None:
    """用户消息含 trigger「续写」时应自动匹配 novel-writing。"""
    context = load_skill_context(user_message="帮我续写一段打斗")
    assert context.id == "novel-writing"
    assert context.display_name == "资深玄幻小说作家"
