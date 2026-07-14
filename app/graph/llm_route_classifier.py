"""LLM 结构化路由分类器（级联 L3 层）。

【职责】
    调用当前 Provider，让模型按 JSON Schema 输出 RouteDecision。
    任何异常（网络、超时、解析失败）都返回 None，
    由 route_cascade.py 回退规则层结果——路由永不阻塞主流程。

【何时被调用】
    app/graph/route_cascade.py 在 hybrid 模式规则置信度不足、
    或 llm 模式下调用 classify()。

【简例】
    classifier = LlmRouteClassifier(provider)
    classifier.classify("张三的师父是谁") -> RouteDecision(needs_project=True, ...)
"""

import logging
from typing import Protocol

from app.graph.llm_route_parser import parse_route_response
from app.graph.llm_route_prompt import ROUTE_TEMPERATURE, build_route_messages
from app.providers.provider_models import ChatCompletionRequest, ChatCompletionResult
from app.schemas.agent_state import RouteDecision

logger = logging.getLogger(__name__)


class ChatProvider(Protocol):
    """分类器依赖的 Provider 最小接口（便于测试注入假实现）。"""

    def chat(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        """执行一次非流式对话调用。"""
        ...


class LlmRouteClassifier:
    """LLM 路由分类器。

    参数说明:
        provider: 满足 ChatProvider 协议的模型调用器
                  （生产为 OpenAICompatibleProvider，测试注入假对象）。
    """

    def __init__(self, provider: ChatProvider) -> None:
        """初始化分类器。"""
        self._provider = provider

    def classify(self, question: str) -> RouteDecision | None:
        """让 LLM 判定路由。

        参数:
            question: 用户问题原文。

        返回:
            RouteDecision | None: 成功返回决策；调用/解析失败返回 None。
        """
        request = ChatCompletionRequest(
            messages=build_route_messages(question),
            temperature=ROUTE_TEMPERATURE,
        )
        try:
            result = self._provider.chat(request)
        except Exception as exc:  # noqa: BLE001 — 路由失败必须降级而非中断对话
            logger.warning("LLM 路由调用失败，将回退规则层：%s", exc)
            return None
        return parse_route_response(result.content)
