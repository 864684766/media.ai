"""从用户 brief 提取澄清维度信号。"""

from dataclasses import dataclass

from app.core.clarification_brief_constants import (
    OPTION_DURATION_M3,
    OPTION_DURATION_S30,
    OPTION_DURATION_S60,
    QUESTION_ID_DURATION,
    QUESTION_ID_PLATFORM,
    QUESTION_ID_STYLE,
)


@dataclass(frozen=True)
class BriefSignals:
    """brief 中已识别到的偏好维度。"""

    duration_option_id: str | None = None
    platform_option_id: str | None = None
    style_option_id: str | None = None
    theme_text: str = ""


def extract_brief_signals(text: str) -> BriefSignals:
    """解析用户 brief，识别已给出的时长/平台/风格/主题。"""
    brief = text.strip()
    return BriefSignals(
        duration_option_id=_infer_duration_option(brief),
        platform_option_id=_infer_platform_option(brief),
        style_option_id=_infer_style_option(brief),
        theme_text=brief,
    )


def signal_for_question(signals: BriefSignals, question_id: str) -> str | None:
    """返回某题在 brief 中已识别的 option_id。"""
    if question_id == QUESTION_ID_DURATION:
        return signals.duration_option_id
    if question_id == QUESTION_ID_PLATFORM:
        return signals.platform_option_id
    if question_id == QUESTION_ID_STYLE:
        return signals.style_option_id
    return None


def _infer_duration_option(brief: str) -> str | None:
    """从 brief 推断时长选项。"""
    if _has_any(brief, ("2-3分钟", "2–3分钟", "两三分钟", "三分钟")):
        return OPTION_DURATION_M3
    if _has_any(brief, ("60秒", "一分钟", "1分钟", "约60")):
        return OPTION_DURATION_S60
    if _has_any(brief, ("30秒", "半分钟", "30s", "30S")):
        return OPTION_DURATION_S30
    return None


def _infer_platform_option(brief: str) -> str | None:
    """从 brief 推断平台选项。"""
    if _has_any(brief, ("抖音", "竖屏", "tiktok")):
        return "douyin"
    if _has_any(brief, ("B站", "b站", "哔哩", "横屏")):
        return "bilibili"
    if _has_any(brief, ("广告片", "广告", "宣传片")):
        return "ad"
    return None


def _infer_style_option(brief: str) -> str | None:
    """从 brief 推断风格选项。"""
    if _has_any(brief, ("动漫", "动画", "卡通", "2D")):
        return "cartoon"
    if _has_any(brief, ("电影感", "cinematic", "大片")):
        return "cinematic"
    if _has_any(brief, ("简约", "产品风", "极简")):
        return "minimal"
    return None


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    """文本是否包含任一关键词（大小写不敏感）。"""
    lower = text.lower()
    return any(word.lower() in lower for word in words)
