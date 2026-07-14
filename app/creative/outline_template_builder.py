"""大纲模板生成（LLM 未接入时的 fallback）。"""

from app.core.clarification_brief_constants import BRIEF_SECTION_USER
from app.core.creative_plan_constants import OUTLINE_CREATION_TYPE_VIDEO
from app.creative.outline_duration_resolver import resolve_video_target_duration_sec
from app.creative.video_segment_builder import build_video_segments
from app.schemas.creative_plan import (
    NovelChapterItem,
    NovelCharacterItem,
    NovelPlanContent,
    VideoPlanContent,
)


def build_outline_content(creation_type: str, summary_md: str) -> dict:
    """按创作类型生成大纲 content 字典。"""
    if creation_type == OUTLINE_CREATION_TYPE_VIDEO:
        return _video_content(summary_md).model_dump()
    return _novel_content(summary_md).model_dump()


def build_outline_title(creation_type: str) -> str:
    """生成默认大纲标题。"""
    if creation_type == OUTLINE_CREATION_TYPE_VIDEO:
        return "视频策划方案 v1"
    return "小说开篇纲要 v1"


def _novel_content(summary_md: str) -> NovelPlanContent:
    """小说大纲模板。"""
    synopsis = _theme_from_summary(summary_md) or "基于用户偏好展开的玄幻开篇故事。"
    return NovelPlanContent(
        synopsis=synopsis,
        chapters=[
            NovelChapterItem(
                chapter_no=1,
                title="命运初启",
                beats=["主角登场", "世界观铺垫", "首个冲突"],
                foreshadowing="埋下主线伏笔",
            ),
        ],
        characters=[
            NovelCharacterItem(name="主角", role="成长型主人公"),
            NovelCharacterItem(name="引路人", role="师父/盟友"),
        ],
    )


def _video_content(summary_md: str) -> VideoPlanContent:
    """视频大纲模板（时长与分段随摘要解析）。"""
    theme = _theme_from_summary(summary_md) or "核心创意"
    duration = resolve_video_target_duration_sec(summary_md)
    hook = f"3 秒内呈现「{theme}」的关键画面。"
    return VideoPlanContent(
        hook=hook,
        segments=build_video_segments(duration, theme),
        style_notes="镜头运动贴合叙事节奏；字幕简洁有力。",
        target_duration_sec=duration,
    )


def _theme_from_summary(summary_md: str) -> str:
    """从摘要中提取用户主题描述。"""
    for line in summary_md.splitlines():
        if BRIEF_SECTION_USER in line:
            return line.split("：", 1)[-1].strip()
    for line in summary_md.splitlines():
        text = line.strip().lstrip("-").strip()
        if text and not text.startswith("#") and "**" in text:
            return text.replace("**", "").split("：", 1)[-1].strip()
    return ""
