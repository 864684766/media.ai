"""从需求摘要解析视频目标时长。"""

import re

from app.core.clarification_brief_constants import (
    DEFAULT_VIDEO_TARGET_DURATION_SEC,
    OPTION_DURATION_M3,
    OPTION_DURATION_S30,
    OPTION_DURATION_S60,
    QUESTION_ID_DURATION,
)

_DURATION_LABEL_TO_SEC = {
    "30秒内": 30,
    "约60秒": 60,
    "2–3分钟": 150,
    "2-3分钟": 150,
}


def resolve_video_target_duration_sec(summary_md: str) -> int:
    """从摘要 Markdown 解析目标时长（秒）。"""
    from_label = _duration_from_summary_label(summary_md)
    if from_label is not None:
        return from_label
    from_brief = _duration_from_user_brief_section(summary_md)
    if from_brief is not None:
        return from_brief
    return DEFAULT_VIDEO_TARGET_DURATION_SEC


def _duration_from_summary_label(summary_md: str) -> int | None:
    """解析 q_duration 行上的选项文案。"""
    for line in summary_md.splitlines():
        if QUESTION_ID_DURATION not in line:
            continue
        for label, sec in _DURATION_LABEL_TO_SEC.items():
            if label in line:
                return sec
        return _map_option_token_to_sec(line)


def _duration_from_user_brief_section(summary_md: str) -> int | None:
    """从用户原始需求段落解析秒数。"""
    match = re.search(r"(\d+)\s*秒", summary_md)
    if match:
        return int(match.group(1))
    return None


def _map_option_token_to_sec(line: str) -> int | None:
    """从 option_id token 推断秒数。"""
    if OPTION_DURATION_S30 in line:
        return 30
    if OPTION_DURATION_S60 in line:
        return 60
    if OPTION_DURATION_M3 in line:
        return 150
    return None
