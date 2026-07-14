"""LLM Grader。

【职责】
    调用 Provider 结构化判定证据相关性；失败返回 None 由上层回退规则版。
"""

import logging
from typing import Protocol

from app.retrieval import grader_constants as gc
from app.retrieval.llm_grader_parser import parse_grader_response
from app.retrieval.llm_grader_prompt import build_grader_messages
from app.retrieval.retrieval_models import GradeResult, RetrievedChunk
from app.providers.provider_models import ChatCompletionRequest, ChatCompletionResult

logger = logging.getLogger(__name__)


class ChatProvider(Protocol):
    """Grader 依赖的 Provider 最小接口。"""

    def chat(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        """执行一次非流式对话。"""
        ...


class LlmGrader:
    """LLM 相关性评估器。"""

    def __init__(self, provider: ChatProvider) -> None:
        """绑定 Provider。"""
        self._provider = provider

    def grade(self, question: str, chunks: list[RetrievedChunk]) -> GradeResult | None:
        """LLM 评估；失败返回 None。"""
        if not chunks:
            from app.retrieval.retrieval_constants import VERDICT_NO_EVIDENCE

            return GradeResult(verdict=VERDICT_NO_EVIDENCE)
        request = self._build_request(question, chunks)
        try:
            result = self._provider.chat(request)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM Grader 调用失败: %s", exc)
            return None
        verdict = parse_grader_response(result.content)
        if verdict is None:
            return None
        return GradeResult(verdict=verdict)

    def _build_request(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> ChatCompletionRequest:
        """构造 Chat 请求。"""
        texts = [chunk.text for chunk in chunks]
        return ChatCompletionRequest(
            messages=build_grader_messages(question, texts),
            temperature=gc.LLM_GRADER_TEMPERATURE,
        )
