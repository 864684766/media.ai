"""Query Rewrite 实现。

【职责】
    Grader 判定 irrelevant 时改写 query 并重试 Hybrid 检索。
"""

import logging
from typing import Protocol

from app.retrieval.query_rewrite_prompt import build_rewrite_messages
from app.providers.provider_models import ChatCompletionRequest, ChatCompletionResult

logger = logging.getLogger(__name__)
REWRITE_TEMPERATURE = 0.2


class ChatProvider(Protocol):
    """改写器依赖的 Provider 最小接口。"""

    def chat(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        """执行一次非流式对话。"""
        ...


class QueryRewriter:
    """检索 query 改写器。"""

    def __init__(self, provider: ChatProvider) -> None:
        """绑定 Provider。"""
        self._provider = provider

    def rewrite(self, question: str, query: str) -> str:
        """改写 query；失败时返回原 query。"""
        request = ChatCompletionRequest(
            messages=build_rewrite_messages(question, query),
            temperature=REWRITE_TEMPERATURE,
        )
        try:
            result = self._provider.chat(request)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Query rewrite 失败，保留原 query: %s", exc)
            return query
        text = result.content.strip()
        return text if text else query


class PassthroughRewriter:
    """无 Provider 时的空改写器（直接返回原 query）。"""

    def rewrite(self, question: str, query: str) -> str:
        """不改写。"""
        return query


def build_query_rewriter(yaml_config: dict | None = None) -> QueryRewriter | PassthroughRewriter:
    """构建改写器；Provider 不可用时用直通实现。"""
    try:
        from app.retrieval.chat_provider_factory import build_chat_provider

        provider = build_chat_provider(yaml_config)
        return QueryRewriter(provider)
    except Exception:  # noqa: BLE001
        return PassthroughRewriter()
