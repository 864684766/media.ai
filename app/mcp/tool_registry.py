"""MCP 工具注册表。"""

from app.mcp.builtin_tools import list_builtin_tools
from app.mcp.tool_models import McpToolDefinition


def discover_tools() -> list[McpToolDefinition]:
    """发现可用 MCP 工具（当前为内置工具）。"""
    raw = list_builtin_tools()
    return [
        McpToolDefinition(name=item["name"], description=item.get("description", ""))
        for item in raw
    ]
