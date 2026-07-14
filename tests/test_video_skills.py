"""视频创作 Skill（director / storyboard）注册测试。

【覆盖点】
    1. discover_skills 能发现三个 Skill（novel-writing / director / storyboard）。
    2. 触发词「分镜」应匹配 storyboard；「运镜」应匹配 director。
    3. 显式 skill_id 加载能读到 system prompt。
"""

from app.skills.registry import discover_skills, load_skill_context


def test_discover_finds_video_skills() -> None:
    """扫描应发现全部三个 Skill 目录。"""
    skill_ids = {skill.skill_id for skill in discover_skills()}
    assert {"novel-writing", "director", "storyboard"}.issubset(skill_ids)


def test_trigger_matches_storyboard() -> None:
    """含「分镜」的消息应自动匹配 storyboard。"""
    context = load_skill_context(user_message="帮我把这段脚本拆成分镜表")
    assert context.id == "storyboard"
    assert "分镜" in context.system_prompt
    assert "json" in context.system_prompt.lower()


def test_trigger_matches_director() -> None:
    """含「运镜」的消息应自动匹配 director。"""
    context = load_skill_context(user_message="这段开场的运镜怎么设计")
    assert context.id == "director"


def test_explicit_skill_id_loads_system_prompt() -> None:
    """显式指定 skill_id=director 应加载导演 system prompt。"""
    context = load_skill_context(skill_id="director")
    assert context.id == "director"
    assert "导演" in context.system_prompt
