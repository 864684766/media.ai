"""OpenAI Chat Completions 兼容 Provider。

【职责】
    将 lanmo 内部的 ChatCompletionRequest 转成 OpenAI 兼容 HTTP 请求。

【覆盖厂商】
    智谱 GLM、DeepSeek、Kimi、本地 vLLM / Ollama OpenAI 兼容服务等。

【测试方式】
    单元测试注入 httpx.MockTransport，不会调用真实模型或消耗 API Key。
"""

from collections.abc import Iterable
from typing import Any

import httpx

from app.providers import provider_constants as pc
from app.providers.provider_errors import classify_provider_error
from app.providers.provider_models import (
    ChatCompletionRequest,
    ChatCompletionResult,
    ModelConfig,
)
from app.providers.openai_stream_parser import parse_openai_stream_chunk, parse_openai_stream_line
from app.providers.provider_stream_models import ProviderStreamChunk


class OpenAICompatibleProvider:
    """OpenAI 兼容模型调用器。

    参数说明:
        config: 当前模型配置（provider/model/api_base/api_key）。
        client: 可选 httpx.Client；测试时注入 MockTransport。
    """

    def __init__(
        self,
        config: ModelConfig,
        client: httpx.Client | None = None,
    ) -> None:
        """初始化 Provider。"""
        self._config = config
        self._client = client if client is not None else _create_default_client()

    def chat(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        """执行一次非流式 Chat Completions 调用。

        参数:
            request: 消息、temperature、stream 等参数。

        返回:
            ChatCompletionResult: assistant 文本与原始 JSON。
        """
        # 步骤 1：把内部请求转成 OpenAI 兼容 JSON
        payload = _build_payload(self._config, request)
        try:
            # 步骤 2：POST 到 {api_base}/chat/completions
            response = self._client.post(
                _build_chat_url(self._config.api_base),
                headers=_build_headers(self._config.api_key),
                json=payload,
            )
            # 步骤 3：HTTP 非 2xx 时抛错，避免后面解析假数据
            response.raise_for_status()
            # 步骤 4：解析 choices[0].message.content
            raw = response.json()
            return ChatCompletionResult(content=_extract_content(raw), raw=raw)
        except Exception as exc:
            raise classify_provider_error(exc) from exc

    def stream_chat(self, request: ChatCompletionRequest) -> Iterable[str]:
        """执行一次流式 Chat Completions 调用。

        参数:
            request: 消息、temperature 等参数；会强制 stream=True。

        返回:
            Iterable[str]: Provider 逐段返回的 delta 文本。
        """
        payload = _build_stream_payload(self._config, request)
        try:
            with self._client.stream(
                "POST",
                _build_chat_url(self._config.api_base),
                headers=_build_headers(self._config.api_key),
                json=payload,
            ) as response:
                response.raise_for_status()
                yield from _iter_stream_deltas(response)
        except Exception as exc:
            raise classify_provider_error(exc) from exc

    def stream_chat_chunks(
        self,
        request: ChatCompletionRequest,
    ) -> Iterable[ProviderStreamChunk]:
        """执行流式调用并返回结构化 chunk。

        参数:
            request: 消息、temperature 等参数；会强制 stream=True。

        返回:
            Iterable[ProviderStreamChunk]: 含 delta / usage 的片段。
        """
        payload = _build_stream_payload(self._config, request)
        try:
            with self._client.stream(
                "POST",
                _build_chat_url(self._config.api_base),
                headers=_build_headers(self._config.api_key),
                json=payload,
            ) as response:
                response.raise_for_status()
                yield from _iter_stream_chunks(response)
        except Exception as exc:
            raise classify_provider_error(exc) from exc


def _create_default_client() -> httpx.Client:
    """创建默认 HTTP Client。"""
    return httpx.Client(timeout=pc.DEFAULT_PROVIDER_TIMEOUT_SECONDS)


def _build_chat_url(api_base: str) -> str:
    """拼接 Chat Completions URL。"""
    return f"{api_base.rstrip('/')}{pc.OPENAI_CHAT_COMPLETIONS_PATH}"


def _build_headers(api_key: str | None) -> dict[str, str]:
    """构造 HTTP Headers；无 key 时也保留 JSON Content-Type。"""
    headers = {pc.CONTENT_TYPE_HEADER_NAME: pc.JSON_CONTENT_TYPE}
    if api_key:
        headers[pc.AUTHORIZATION_HEADER_NAME] = f"{pc.BEARER_TOKEN_PREFIX} {api_key}"
    return headers


def _build_payload(
    config: ModelConfig,
    request: ChatCompletionRequest,
) -> dict[str, Any]:
    """构造 OpenAI 兼容请求体。"""
    return {
        pc.OPENAI_FIELD_MODEL: config.model,
        pc.OPENAI_FIELD_MESSAGES: [message.model_dump() for message in request.messages],
        pc.OPENAI_FIELD_TEMPERATURE: request.temperature,
        pc.OPENAI_FIELD_STREAM: request.stream,
    }


def _build_stream_payload(
    config: ModelConfig,
    request: ChatCompletionRequest,
) -> dict[str, Any]:
    """构造流式 OpenAI 兼容请求体。"""
    payload = _build_payload(config, request)
    payload[pc.OPENAI_FIELD_STREAM] = True
    return payload


def _iter_stream_deltas(response: httpx.Response) -> Iterable[str]:
    """从 httpx Response 逐行解析 delta 文本。"""
    for line in response.iter_lines():
        delta = parse_openai_stream_line(line)
        if delta is not None:
            yield delta


def _iter_stream_chunks(response: httpx.Response) -> Iterable[ProviderStreamChunk]:
    """从 httpx Response 逐行解析结构化 chunk。"""
    for line in response.iter_lines():
        chunk = parse_openai_stream_chunk(line)
        if chunk is not None:
            yield chunk


def _extract_content(raw_response: dict[str, Any]) -> str:
    """从 OpenAI 兼容响应中提取 assistant 文本。"""
    choices = raw_response.get(pc.OPENAI_FIELD_CHOICES, [])
    if not choices:
        return ""
    message = choices[0].get(pc.OPENAI_FIELD_MESSAGE, {})
    content = message.get(pc.OPENAI_FIELD_CONTENT, "")
    return content if isinstance(content, str) else ""
