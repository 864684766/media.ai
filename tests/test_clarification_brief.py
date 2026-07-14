"""澄清 brief 提取与大纲时长解析单元测试。"""

from app.creative.clarification_brief_extractor import extract_brief_signals
from app.creative.clarification_question_filter import filter_questions_by_brief
from app.creative.clarification_templates import build_template_questions
from app.creative.outline_duration_resolver import resolve_video_target_duration_sec
from app.creative.outline_template_builder import build_outline_content
from app.core.clarification_brief_constants import (
    OPTION_DURATION_S30,
    QUESTION_ID_DURATION,
    QUESTION_ID_PLATFORM,
    QUESTION_ID_STYLE,
)


def test_brief_extracts_30s_and_cartoon_style() -> None:
    """用户 brief 含 30 秒与动画时应识别时长与风格。"""
    signals = extract_brief_signals("生成一个龟兔赛跑的30秒动画")
    assert signals.duration_option_id == OPTION_DURATION_S30
    assert signals.style_option_id == "cartoon"
    assert signals.platform_option_id is None


def test_filter_skips_duration_and_style_questions() -> None:
    """已写在 brief 中的维度不应再出现在问卷。"""
    brief = "生成一个龟兔赛跑的30秒动画"
    signals = extract_brief_signals(brief)
    shown = filter_questions_by_brief(build_template_questions("video"), signals)
    ids = {q.question_id for q in shown}
    assert QUESTION_ID_DURATION not in ids
    assert QUESTION_ID_STYLE not in ids
    assert QUESTION_ID_PLATFORM in ids


def test_outline_uses_30s_from_summary() -> None:
    """大纲分段目标时长应跟随 q_duration 与用户 brief。"""
    summary = (
        "## 创作需求摘要（video）\n\n"
        "**用户原始需求**：生成一个龟兔赛跑的30秒动画\n\n"
        "- **q_duration**：30秒内\n"
        "- **q_style**：动漫\n"
    )
    assert resolve_video_target_duration_sec(summary) == 30
    content = build_outline_content("video", summary)
    assert content["target_duration_sec"] == 30
    assert content["segments"][-1]["end_sec"] == 30
    assert "龟兔赛跑" in content["hook"]
