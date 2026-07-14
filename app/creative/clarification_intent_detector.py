"""澄清意图判定（纯规则）。

【职责】
    判断是否应对本轮 Chat 弹出结构化澄清题。

【何时调用】
    clarification_stream_service 在 Provider 生成前调用。
"""

from app.core.clarification_constants import CREATION_TYPE_NOVEL, CREATION_TYPE_VIDEO
from app.core.creative_config_reader import ClarificationConfig
from app.schemas.chat import ChatRequest

_NEW_CREATION_KEYWORDS = ("大纲", "策划", "写一", "创作", "开篇", "新故事", "宣传片", "短视频", "分镜表")
_SKIP_KEYWORDS = ("润色", "改稿", "改短", "续写", "师父", "设定", "原文")
_QUERY_KEYWORDS = ("是谁", "什么", "查询", "检索")


def should_start_clarification(request: ChatRequest, cfg: ClarificationConfig) -> bool:
    """是否应发起新一轮澄清。

    参数:
        request: Chat 请求。
        cfg: 澄清配置。

    返回:
        bool: True 表示应推 clarification_request。
    """
    if not cfg.enabled or request.clarification_response is not None:
        return False
    if request.clarification_skip:
        return False
    if request.creation_type not in (CREATION_TYPE_NOVEL, CREATION_TYPE_VIDEO):
        return False
    text = request.message.strip()
    if not text:
        return False
    if _has_any(text, _SKIP_KEYWORDS) and not _has_any(text, _NEW_CREATION_KEYWORDS):
        return False
    if _has_any(text, _QUERY_KEYWORDS) and not _has_any(text, _NEW_CREATION_KEYWORDS):
        return False
    if _has_any(text, _NEW_CREATION_KEYWORDS):
        return True
    return len(text) < cfg.min_brief_chars


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    """文本是否包含任一关键词。"""
    return any(word in text for word in words)
