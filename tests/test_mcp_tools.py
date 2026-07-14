"""MCP 内置工具测试。"""

import pytest

from app.mcp.builtin_tools import run_builtin_tool
from app.mcp.client import McpClient


def test_builtin_echo_tool() -> None:
    """echo 工具应回显参数。"""
    result = run_builtin_tool("echo", {"text": "hi"})
    assert result["echo"]["text"] == "hi"


def test_mcp_client_disabled_raises() -> None:
    """未启用时 call_tool 应抛 RuntimeError。"""
    client = McpClient(enabled=False, servers=[])
    with pytest.raises(RuntimeError):
        client.call_tool("echo", {})


def test_mcp_client_lists_tools_when_enabled() -> None:
    """启用时应返回内置工具列表。"""
    client = McpClient(enabled=True, servers=[])
    tools = client.list_tools()
    assert any(tool["name"] == "echo" for tool in tools)
