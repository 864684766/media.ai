"""web_search 配置读取器。

【职责】
    从 config/app.yaml 的 web_search 段读取 provider 与 max_results，
    让 config 中的 web_search 配置真正生效。
"""

from typing import Any

from app.core.config_yaml_loader import load_app_yaml

# app.yaml 顶层段名与键名
YAML_KEY_WEB_SEARCH_SECTION = "web_search"
YAML_KEY_PROVIDER = "provider"
YAML_KEY_MAX_RESULTS = "max_results"

# 默认值：provider 用 tavily，最多 5 条结果
DEFAULT_PROVIDER = "tavily"
DEFAULT_MAX_RESULTS = 5


def load_web_search_settings(yaml_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """读取 web_search 配置。

    参数:
        yaml_config: 测试可传入假配置；None 时读取 config/app.yaml。

    返回:
        dict: {"provider": str, "max_results": int}。
    """
    app_config = yaml_config if yaml_config is not None else load_app_yaml()
    raw = app_config.get(YAML_KEY_WEB_SEARCH_SECTION, {})
    section = raw if isinstance(raw, dict) else {}
    provider = section.get(YAML_KEY_PROVIDER, DEFAULT_PROVIDER)
    max_results = section.get(YAML_KEY_MAX_RESULTS, DEFAULT_MAX_RESULTS)
    return {
        YAML_KEY_PROVIDER: provider if isinstance(provider, str) else DEFAULT_PROVIDER,
        YAML_KEY_MAX_RESULTS: max_results if isinstance(max_results, int) and max_results > 0 else DEFAULT_MAX_RESULTS,
    }
