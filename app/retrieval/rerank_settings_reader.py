"""Rerank 配置读取器。"""

from typing import Any

from app.core.config_yaml_loader import load_app_yaml

YAML_KEY_RERANK_SECTION = "rerank"
YAML_KEY_RERANK_PROVIDER = "provider"
RERANK_PROVIDER_LOCAL = "local"
RERANK_PROVIDER_SEMANTIC = "semantic"
DEFAULT_RERANK_PROVIDER = RERANK_PROVIDER_SEMANTIC


def load_rerank_provider(yaml_config: dict[str, Any] | None = None) -> str:
    """读取 rerank provider（local / semantic）。"""
    config = yaml_config if yaml_config is not None else load_app_yaml()
    section = config.get(YAML_KEY_RERANK_SECTION, {})
    if not isinstance(section, dict):
        return DEFAULT_RERANK_PROVIDER
    provider = str(section.get(YAML_KEY_RERANK_PROVIDER, DEFAULT_RERANK_PROVIDER))
    if provider in (RERANK_PROVIDER_LOCAL, RERANK_PROVIDER_SEMANTIC):
        return provider
    return DEFAULT_RERANK_PROVIDER
