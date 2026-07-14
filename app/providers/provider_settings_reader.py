"""Provider 配置读取器。

【职责】
    把 config/app.yaml 的 model 段和 .env 的 API Key 合并成 ModelConfig。

【分工】
    app.yaml：provider / model / api_base（非密钥）
    .env：ZHIPU_API_KEY / DEEPSEEK_API_KEY / KIMI_API_KEY（密钥）

【示例】
    model.provider=zhipu + ZHIPU_API_KEY=xxx → ModelConfig(provider="zhipu", api_key="xxx")
"""

from typing import Any

from app.core.config import settings
from app.core.config_yaml_loader import load_app_yaml
from app.providers import provider_constants as pc
from app.providers.provider_models import ModelConfig


def load_model_config(yaml_config: dict[str, Any] | None = None) -> ModelConfig:
    """读取当前模型配置。

    参数:
        yaml_config: 测试可传入假 app.yaml；为 None 时读取真实 config/app.yaml。

    返回:
        ModelConfig: Provider Registry 可直接使用的配置对象。
    """
    app_config = yaml_config if yaml_config is not None else load_app_yaml()
    model_section = _read_model_section(app_config)
    provider_id = _read_provider_id(model_section)
    return ModelConfig(
        provider=provider_id,
        model=_read_model_name(model_section),
        api_base=_read_api_base(model_section, provider_id),
        api_key=_read_api_key(provider_id),
    )


def _read_model_section(app_config: dict[str, Any]) -> dict[str, Any]:
    """读取 app.yaml 的 model 段。"""
    raw = app_config.get(pc.YAML_KEY_MODEL_SECTION, {})
    return raw if isinstance(raw, dict) else {}


def _read_provider_id(model_section: dict[str, Any]) -> str:
    """读取 provider id；缺省为 zhipu。"""
    raw = model_section.get(pc.YAML_KEY_PROVIDER, pc.PROVIDER_ID_ZHIPU)
    return raw.strip() if isinstance(raw, str) else pc.PROVIDER_ID_ZHIPU


def _read_model_name(model_section: dict[str, Any]) -> str:
    """读取模型名；缺省为 glm-4-flash。"""
    raw = model_section.get(pc.YAML_KEY_MODEL, "glm-4-flash")
    return raw.strip() if isinstance(raw, str) else "glm-4-flash"


def _read_api_base(model_section: dict[str, Any], provider_id: str) -> str:
    """读取 api_base；未配置时按 provider 给默认值。"""
    raw = model_section.get(pc.YAML_KEY_API_BASE)
    if isinstance(raw, str) and raw.strip():
        return raw.rstrip("/")
    return _default_api_base(provider_id)


def _default_api_base(provider_id: str) -> str:
    """根据 provider id 返回默认 OpenAI 兼容地址。"""
    defaults = {
        pc.PROVIDER_ID_ZHIPU: pc.DEFAULT_ZHIPU_API_BASE,
        pc.PROVIDER_ID_DEEPSEEK: pc.DEFAULT_DEEPSEEK_API_BASE,
        pc.PROVIDER_ID_KIMI: pc.DEFAULT_KIMI_API_BASE,
        pc.PROVIDER_ID_LOCAL_OPENAI: pc.DEFAULT_LOCAL_OPENAI_API_BASE,
    }
    return defaults.get(provider_id, pc.DEFAULT_ZHIPU_API_BASE)


def _read_api_key(provider_id: str) -> str | None:
    """根据 provider id 从 .env 读取对应 API Key。"""
    api_keys = {
        pc.PROVIDER_ID_ZHIPU: settings.zhipu_api_key,
        pc.PROVIDER_ID_DEEPSEEK: settings.deepseek_api_key,
        pc.PROVIDER_ID_KIMI: settings.kimi_api_key,
    }
    return api_keys.get(provider_id)
