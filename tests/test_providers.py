"""Provider Registry 单元测试（不调用真实模型）。"""

import httpx
import pytest

from app.providers import (
    ChatCompletionRequest,
    ChatMessage,
    ModelConfig,
    ProviderRegistry,
    create_default_provider_registry,
)
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.provider_settings_reader import load_model_config


def test_load_model_config_from_yaml() -> None:
    """从 app.yaml 字典读取 provider/model/api_base。"""
    config = load_model_config(
        {
            "model": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "api_base": "https://api.deepseek.com/v1/",
            }
        }
    )
    assert config.provider == "deepseek"
    assert config.model == "deepseek-chat"
    assert config.api_base == "https://api.deepseek.com/v1"


def test_default_registry_builds_zhipu_provider() -> None:
    """默认 Registry 应能构建 zhipu OpenAI 兼容 Provider。"""
    registry = create_default_provider_registry()
    config = ModelConfig(
        provider="zhipu",
        model="glm-4-flash",
        api_base="https://example.test/v1",
    )
    provider = registry.build(config)
    assert isinstance(provider, OpenAICompatibleProvider)


def test_registry_raises_for_unknown_provider() -> None:
    """未知 provider 应明确报错，避免静默走错模型。"""
    registry = ProviderRegistry()
    config = ModelConfig(
        provider="unknown",
        model="unknown-model",
        api_base="https://example.test/v1",
    )
    with pytest.raises(ValueError, match="未注册 Provider"):
        registry.build(config)


def test_openai_compatible_chat_with_mock_transport() -> None:
    """使用 MockTransport 验证请求格式与响应解析。"""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["json"] = request.read().decode("utf-8")
        return httpx.Response(200, json=_mock_chat_response())

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleProvider(_fake_model_config(), client=client)
    result = provider.chat(_fake_chat_request())
    assert result.content == "测试回复"
    assert captured["url"] == "https://example.test/v1/chat/completions"


def test_openai_compatible_stream_chat_with_mock_transport() -> None:
    """使用 MockTransport 验证流式 delta 解析。"""

    def handler(request: httpx.Request) -> httpx.Response:
        stream_text = "\n\n".join(
            [
                'data: {"choices":[{"delta":{"content":"你"}}]}',
                'data: {"choices":[{"delta":{"content":"好"}}]}',
                "data: [DONE]",
            ]
        )
        return httpx.Response(200, text=stream_text)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleProvider(_fake_model_config(), client=client)
    chunks = list(provider.stream_chat(_fake_chat_request()))
    assert chunks == ["你", "好"]


def test_openai_compatible_stream_chat_chunks_with_usage() -> None:
    """结构化流式接口应返回 delta 与 usage。"""

    def handler(request: httpx.Request) -> httpx.Response:
        stream_text = "\n\n".join(
            [
                'data: {"choices":[{"delta":{"content":"你"}}]}',
                'data: {"choices":[],"usage":{"total_tokens":9}}',
                "data: [DONE]",
            ]
        )
        return httpx.Response(200, text=stream_text)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleProvider(_fake_model_config(), client=client)
    chunks = list(provider.stream_chat_chunks(_fake_chat_request()))
    assert chunks[0].delta == "你"
    assert chunks[1].usage == {"total_tokens": 9}


def test_openai_compatible_chat_classifies_http_error() -> None:
    """HTTP 401 应被分类为 provider_auth_error。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="bad key")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleProvider(_fake_model_config(), client=client)
    with pytest.raises(Exception) as exc_info:
        provider.chat(_fake_chat_request())
    assert getattr(exc_info.value, "code") == "provider_auth_error"


def _fake_model_config() -> ModelConfig:
    """构造测试用模型配置。"""
    return ModelConfig(
        provider="zhipu",
        model="glm-4-flash",
        api_base="https://example.test/v1",
        api_key="test-key",
    )


def _fake_chat_request() -> ChatCompletionRequest:
    """构造测试用 Chat 请求。"""
    return ChatCompletionRequest(
        messages=[ChatMessage(role="user", content="你好")],
        temperature=0.1,
    )


def _mock_chat_response() -> dict:
    """OpenAI 兼容响应最小样例。"""
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "测试回复",
                }
            }
        ]
    }
