"""大纲 content JSON → Markdown 渲染。"""

from app.core.creative_plan_constants import OUTLINE_CREATION_TYPE_VIDEO
from app.schemas.creative_plan import NovelPlanContent, VideoPlanContent


def render_content_md(creation_type: str, content: dict) -> str:
    """将结构化 content 转为可读 Markdown。

    参数:
        creation_type: novel | video。
        content: content_json 解析后的字典。

    返回:
        str: 前端展示用 Markdown。
    """
    if creation_type == OUTLINE_CREATION_TYPE_VIDEO:
        return _render_video(VideoPlanContent.model_validate(content))
    return _render_novel(NovelPlanContent.model_validate(content))


def _render_novel(model: NovelPlanContent) -> str:
    """渲染小说大纲 Markdown。"""
    lines = ["## 故事梗概", model.synopsis, "", "## 章节纲要"]
    for chapter in model.chapters:
        lines.append(f"### 第 {chapter.chapter_no} 章 · {chapter.title}")
        for beat in chapter.beats:
            lines.append(f"- {beat}")
        if chapter.foreshadowing:
            lines.append(f"- 伏笔：{chapter.foreshadowing}")
    lines.extend(["", "## 主要角色"])
    for char in model.characters:
        lines.append(f"- **{char.name}**：{char.role}")
    return "\n".join(lines)


def _render_video(model: VideoPlanContent) -> str:
    """渲染视频大纲 Markdown。"""
    lines = [
        "## 开场钩子",
        model.hook,
        "",
        f"## 分段方案（目标 {model.target_duration_sec}s）",
    ]
    for seg in model.segments:
        lines.append(f"### {seg.start_sec}–{seg.end_sec}s · {seg.mood}")
        lines.append(f"- 画面：{seg.visual}")
    if model.style_notes:
        lines.extend(["", "## 风格说明", model.style_notes])
    return "\n".join(lines)
