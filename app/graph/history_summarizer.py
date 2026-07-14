"""历史 LLM 摘要器。"""

import logging
from typing import Protocol

from app.graph import history_constants as hc
from app.graph.history_compactor_prompt import build_summary_messages
from app.providers.provider_models import ChatCompletionRequest, ChatCompletionResult
from app.schemas.agent_state import ChatHistoryMessage

logger = logging.getLogger(__name__)


class ChatProvider(Protocol):
    """摘要器依赖的 Provider 最小接口。"""

    def chat(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        """执行一次非流式对话。"""
        ...


class HistorySummarizer:
    """调用 LLM 生成历史摘要。"""

    def __init__(self, provider: ChatProvider) -> None:
        """绑定 Provider。"""
        self._provider = provider

    def summarize(self, messages: list[ChatHistoryMessage]) -> str:
        """生成摘要；失败返回空串。"""
        if not messages:
            return ""
        request = ChatCompletionRequest(
            messages=build_summary_messages(messages),
            temperature=hc.HISTORY_SUMMARY_TEMPERATURE,
        )
        try:
            result = self._provider.chat(request)
        except Exception as exc:  # noqa: BLE001
            logger.warning("历史摘要失败: %s", exc)
            return ""
        return result.content.strip()


class TruncationSummarizer:
    """无 Provider 时的截断摘要（取前几条首句）。"""

    def summarize(self, messages: list[ChatHistoryMessage]) -> str:
        """截断式摘要。"""
        parts = [f"{item.role}:{item.content[:80]}" for item in messages[:4]]
        return "；".join(parts)
