"""按目标时长生成分段方案。"""

from app.schemas.creative_plan import VideoSegmentItem

_HOOK_RATIO = 0.17
_CORE_RATIO = 0.55


def build_video_segments(total_sec: int, theme_hint: str) -> list[VideoSegmentItem]:
    """按总时长切分 hook / 核心 / 收尾三段。"""
    hook_end = max(int(total_sec * _HOOK_RATIO), 1)
    core_end = max(int(total_sec * (_HOOK_RATIO + _CORE_RATIO)), hook_end + 1)
    core_end = min(core_end, total_sec - 1) if total_sec > 2 else total_sec
    subject = theme_hint.strip() or "核心内容"
    return [
        VideoSegmentItem(
            start_sec=0,
            end_sec=hook_end,
            visual=f"{subject} — 开场抓注意力",
            mood="紧张期待",
        ),
        VideoSegmentItem(
            start_sec=hook_end,
            end_sec=core_end,
            visual=f"{subject} — 情节/卖点展开",
            mood="节奏上扬",
        ),
        VideoSegmentItem(
            start_sec=core_end,
            end_sec=total_sec,
            visual=f"{subject} — 收束与行动号召",
            mood="高潮收束",
        ),
    ]
