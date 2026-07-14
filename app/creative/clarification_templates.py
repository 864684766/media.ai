"""澄清题目模板（novel / video）。

【职责】
    提供首版固定维度题目；LLM 未接入时作为权威 fallback。

【何时调用】
    clarification_question_builder 构建 SSE questions 列表。
"""

from app.core.clarification_constants import CREATION_TYPE_NOVEL, CREATION_TYPE_VIDEO
from app.schemas.clarification import ClarificationQuestionItem


def build_template_questions(creation_type: str) -> list[ClarificationQuestionItem]:
    """按创作类型返回模板题目列表。

    参数:
        creation_type: novel | video。

    返回:
        list[ClarificationQuestionItem]: 题目列表。
    """
    if creation_type == CREATION_TYPE_VIDEO:
        return _video_questions()
    return _novel_questions()


def _novel_questions() -> list[ClarificationQuestionItem]:
    """小说澄清题模板。"""
    return [
        _q("q_genre", "希望的主类型？", [("xuanhuan", "玄幻修仙"), ("dushi", "都市现实"), ("kehuan", "科幻")]),
        _q("q_tone", "整体基调？", [("hot", "热血升级"), ("dark", "暗黑悬疑"), ("light", "轻松日常")]),
        _q("q_length", "预期篇幅？", [("short", "短篇/开篇"), ("serial", "连载长篇")]),
    ]


def _video_questions() -> list[ClarificationQuestionItem]:
    """视频澄清题模板。"""
    return [
        _q("q_platform", "主要投放平台？", [("douyin", "抖音竖屏"), ("bilibili", "B站横屏"), ("ad", "广告片")]),
        _q("q_duration", "目标时长？", [("s30", "30秒内"), ("s60", "约60秒"), ("m3", "2–3分钟")]),
        _q("q_style", "视觉风格？", [("cinematic", "电影感"), ("cartoon", "动漫"), ("minimal", "简约产品风")]),
    ]


def _q(
    qid: str,
    prompt: str,
    options: list[tuple[str, str]],
) -> ClarificationQuestionItem:
    """构造单题。"""
    from app.schemas.clarification import ClarificationOptionItem

    return ClarificationQuestionItem(
        question_id=qid,
        prompt=prompt,
        options=[ClarificationOptionItem(option_id=oid, label=label) for oid, label in options],
    )
