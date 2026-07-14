"""创作类型分流测试。"""

from app.core.creation_type_constants import CREATION_TYPE_NOVEL, CREATION_TYPE_VIDEO
from app.skills.registry import load_skill_context


def test_creation_type_novel_loads_novel_writing() -> None:
    """小说类型应限定在 novel-writing Skill 池。"""
    context = load_skill_context(
        user_message="帮我写一个童话故事",
        creation_type=CREATION_TYPE_NOVEL,
    )
    assert context.id == "novel-writing"
    assert "小说" in context.system_prompt or "创作" in context.system_prompt


def test_creation_type_video_defaults_director() -> None:
    """视频类型无 trigger 时应默认 director。"""
    context = load_skill_context(
        user_message="帮我设计一段开场",
        creation_type=CREATION_TYPE_VIDEO,
    )
    assert context.id == "director"


def test_creation_type_video_trigger_storyboard() -> None:
    """视频类型下含分镜 trigger 应匹配 storyboard。"""
    context = load_skill_context(
        user_message="帮我把脚本拆成分镜表",
        creation_type=CREATION_TYPE_VIDEO,
    )
    assert context.id == "storyboard"
