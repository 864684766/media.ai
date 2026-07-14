"""LLM Provider 模块。

【职责】
    通过 Provider Registry 屏蔽智谱、DeepSeek、Kimi 等厂商差异。

【常用入口】
    build_current_provider()：读取 config/app.yaml 构建当前模型 Provider。
"""

from app.providers.provider_models import (
    ChatCompletionRequest,
    ChatCompletionResult,
    ChatMessage,
    ModelConfig,
    ProviderHealthResult,
)
from app.providers.provider_health_checker import check_provider_health
from app.providers.registry import (
    ProviderRegistry,
    build_current_provider,
    create_default_provider_registry,
)

__all__ = [
    "ChatCompletionRequest",
    "ChatCompletionResult",
    "ChatMessage",
    "ModelConfig",
    "ProviderRegistry",
    "ProviderHealthResult",
    "build_current_provider",
    "check_provider_health",
    "create_default_provider_registry",
]
