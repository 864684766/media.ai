"""检索链 Provider 工厂辅助。"""

from app.providers.registry import create_default_provider_registry
from app.providers.provider_settings_reader import load_model_config


def build_chat_provider(yaml_config: dict | None = None):
    """按 yaml 构建 Chat Provider。

    参数:
        yaml_config: 测试可传入假 app.yaml。

    返回:
        OpenAICompatibleProvider: Provider 实例。
    """
    config = load_model_config(yaml_config)
    registry = create_default_provider_registry()
    return registry.build(config)
