"""LLM 结构化路由的提示词构造。

【职责】
    生成让模型「只输出 JSON」的分类提示词。
    输出字段与 RouteDecision 契约对齐（sec-15），由 llm_route_parser.py 解析。

【何时被调用】
    app/graph/llm_route_classifier.py 调 Provider 前构造 messages。

【简例】
    build_route_messages("张三的师父是谁")
    -> [ChatMessage(role="system", ...), ChatMessage(role="user", ...)]
"""

from app.core.constants import ROLE_SYSTEM, ROLE_USER
from app.providers.provider_models import ChatMessage

# 分类任务的系统提示词：强制只输出 JSON，字段与 RouteDecision 对齐
ROUTE_SYSTEM_PROMPT = """你是一个意图路由器，为「小说/视频创作 Agent」判断用户问题需要哪些能力。

只输出一个 JSON 对象，不要输出任何其他文字、解释或 Markdown 代码块。字段：
- needs_project (bool): 是否需要查询用户作品库/小说设定（人物、章节、世界观等）
- needs_web (bool): 是否需要联网查询实时/外部信息（新闻、天气、时效性事实）
- needs_creative (bool): 是否需要创作/续写/润色/改稿
- sub_queries (string[]): 若 needs_project 为 true，给出 1-3 个适合检索的短查询；否则为空数组
- reason (string): 一句话中文说明判定依据

示例输出：
{"needs_project": true, "needs_web": false, "needs_creative": true, "sub_queries": ["张三 师父"], "reason": "既要查人物设定又要续写"}"""

# 用户消息模板：只带问题本身（历史与 Skill 上下文为后续增强）
ROUTE_USER_TEMPLATE = "用户问题：{question}"

# 分类任务用低温度，保证输出稳定可解析
ROUTE_TEMPERATURE = 0.0


def build_route_messages(question: str) -> list[ChatMessage]:
    """构造路由分类的对话消息。

    参数:
        question: 用户问题原文。

    返回:
        list[ChatMessage]: system + user 两条消息。
    """
    return [
        ChatMessage(role=ROLE_SYSTEM, content=ROUTE_SYSTEM_PROMPT),
        ChatMessage(role=ROLE_USER, content=ROUTE_USER_TEMPLATE.format(question=question)),
    ]
