"""MCP Client 空 Stub 测试。

【覆盖点】
    1. 默认配置（mcp.enabled: false）下 Client 处于禁用态。
    2. 禁用态调用工具应抛出带引导信息的 RuntimeError。
    3. 启用态但未实现时抛 NotImplementedError（Phase 3 占位）。
    4. 配置段缺失/类型错误时安全回落默认值。
"""

import pytest

from app.mcp import build_mcp_client
from app.mcp.mcp_settings_reader import load_mcp_settings


def test_default_config_disables_mcp() -> None:
    """仓库默认配置 mcp.enabled: false，Client 应为禁用态。"""
    client = build_mcp_client()
    assert client.is_enabled is False
    assert client.list_tools() == []


def test_disabled_client_raises_on_call_tool() -> None:
    """禁用态调用工具应抛 RuntimeError 并包含配置引导。"""
    client = build_mcp_client({"mcp": {"enabled": False}})
    with pytest.raises(RuntimeError, match="mcp.enabled"):
        client.call_tool("filesystem.write", {"path": "a.md"})


def test_enabled_client_unknown_tool_raises() -> None:
    """启用态调用未知工具应抛 ValueError。"""
    client = build_mcp_client({"mcp": {"enabled": True}})
    with pytest.raises(ValueError, match="未知内置工具"):
        client.call_tool("filesystem.write", {"path": "a.md"})


def test_missing_section_falls_back_to_defaults() -> None:
    """mcp 段缺失或类型错误时应回落 enabled=False、servers=[]。"""
    settings = load_mcp_settings({})
    assert settings["enabled"] is False
    assert settings["servers"] == []
    settings = load_mcp_settings({"mcp": "oops"})
    assert settings["enabled"] is False
