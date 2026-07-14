"""MCP Client（Phase 3：内置工具 + 外部 Server 预留）。

【职责】
    mcp.enabled=true 时提供 list_tools / call_tool；
    当前实现内置 echo / list_project_docs，外部 Server 仍预留。
"""

from typing import Any

from app.mcp import mcp_constants as mc
from app.mcp.mcp_settings_reader import load_mcp_settings
from app.mcp.tool_executor import execute_tool
from app.mcp.tool_registry import discover_tools


class McpClient:
    """MCP Client。"""

    def __init__(self, enabled: bool, servers: list) -> None:
        """初始化 Client。"""
        self._enabled = enabled
        self._servers = servers

    @property
    def is_enabled(self) -> bool:
        """返回 MCP 是否启用。"""
        return self._enabled

    def list_tools(self) -> list[dict]:
        """列出可用工具。"""
        if not self._enabled:
            return []
        return [tool.model_dump() for tool in discover_tools()]

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """调用工具。"""
        if not self._enabled:
            raise RuntimeError(mc.MCP_DISABLED_MESSAGE)
        return execute_tool(tool_name, arguments)


def build_mcp_client(yaml_config: dict | None = None) -> McpClient:
    """按配置构造 MCP Client。"""
    settings = load_mcp_settings(yaml_config)
    return McpClient(
        enabled=settings[mc.YAML_KEY_ENABLED],
        servers=settings[mc.YAML_KEY_SERVERS],
    )
