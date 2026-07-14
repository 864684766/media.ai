"""MCP 配置读取器。

【职责】
    从 config/app.yaml 的 mcp 段读取 enabled 与 servers。

【何时被调用】
    app/mcp/client.py 的 build_mcp_client() 组装 Client 时调用。

【简例】
    load_mcp_settings() -> {"enabled": False, "servers": []}
"""

from typing import Any

from app.core.config_yaml_loader import load_app_yaml
from app.mcp import mcp_constants as mc


def load_mcp_settings(yaml_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """读取 MCP 配置。

    参数:
        yaml_config: 测试可传入假配置；None 时读取 config/app.yaml。

    返回:
        dict: {"enabled": bool, "servers": list}。
    """
    app_config = yaml_config if yaml_config is not None else load_app_yaml()
    section = _read_mcp_section(app_config)
    return {
        mc.YAML_KEY_ENABLED: _read_enabled(section),
        mc.YAML_KEY_SERVERS: _read_servers(section),
    }


def _read_mcp_section(app_config: dict[str, Any]) -> dict[str, Any]:
    """读取 mcp 段；缺失或类型不对时返回空 dict。"""
    raw = app_config.get(mc.YAML_KEY_MCP_SECTION, {})
    return raw if isinstance(raw, dict) else {}


def _read_enabled(section: dict[str, Any]) -> bool:
    """读取 enabled 开关；非布尔值时回落默认值 False。"""
    raw = section.get(mc.YAML_KEY_ENABLED, mc.DEFAULT_ENABLED)
    return raw if isinstance(raw, bool) else mc.DEFAULT_ENABLED


def _read_servers(section: dict[str, Any]) -> list:
    """读取 servers 列表；非列表时回落空列表。"""
    raw = section.get(mc.YAML_KEY_SERVERS, [])
    return raw if isinstance(raw, list) else []
