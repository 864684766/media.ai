"""Provider Registry。

【职责】
    根据 model.provider 选择 Provider 适配器，隐藏厂商差异。

【当前实现】
    zhipu / deepseek / kimi / local-openai-compatible 都走 OpenAICompatibleProvider。

【后续扩展】
    Claude 等非 OpenAI 协议厂商可新增 AnthropicCompatibleProvider 并 register。
"""

from collections.abc import Callable

import httpx

from app.providers import provider_constants as pc
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.provider_models import ModelConfig
from app.providers.provider_settings_reader import load_model_config

ProviderFactory = Callable[[ModelConfig, httpx.Client | None], OpenAICompatibleProvider]


class ProviderRegistry:
    """Provider 注册表。

    参数说明:
        factories: provider id 到工厂函数的映射。
    """

    def __init__(self) -> None:
        """创建空注册表。"""
        self._factories: dict[str, ProviderFactory] = {}

    def register(self, provider_id: str, factory: ProviderFactory) -> None:
        """注册一个 provider 工厂。

        参数:
            provider_id: 配置中的 model.provider。
            factory: 创建 Provider 实例的函数。
        """
        self._factories[provider_id] = factory

    def build(
        self,
        config: ModelConfig,
        client: httpx.Client | None = None,
    ) -> OpenAICompatibleProvider:
        """按 config.provider 构建 Provider。

        参数:
            config: 当前模型配置。
            client: 测试用可选 HTTP Client。

        返回:
            OpenAICompatibleProvider: 当前选中的 Provider。
        """
        factory = self._factories.get(config.provider)
        if factory is None:
            raise ValueError(f"未注册 Provider：{config.provider}")
        return factory(config, client)


def create_default_provider_registry() -> ProviderRegistry:
    """创建默认注册表（注册 OpenAI 兼容厂商）。"""
    registry = ProviderRegistry()
    for provider_id in _openai_compatible_provider_ids():
        registry.register(provider_id, _openai_compatible_factory)
    return registry


def build_current_provider(
    client: httpx.Client | None = None,
) -> OpenAICompatibleProvider:
    """读取 config/app.yaml 并构建当前 Provider。

    参数:
        client: 测试用可选 HTTP Client。

    返回:
        OpenAICompatibleProvider: 当前 Provider 实例。
    """
    config = load_model_config()
    registry = create_default_provider_registry()
    return registry.build(config, client)


def _openai_compatible_provider_ids() -> tuple[str, ...]:
    """返回走 OpenAI 兼容协议的 provider id。"""
    return (
        pc.PROVIDER_ID_ZHIPU,
        pc.PROVIDER_ID_DEEPSEEK,
        pc.PROVIDER_ID_KIMI,
        pc.PROVIDER_ID_LOCAL_OPENAI,
    )


def _openai_compatible_factory(
    config: ModelConfig,
    client: httpx.Client | None,
) -> OpenAICompatibleProvider:
    """构建 OpenAICompatibleProvider。"""
    return OpenAICompatibleProvider(config=config, client=client)
