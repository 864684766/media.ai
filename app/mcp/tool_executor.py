"""MCP 工具执行器。"""

from typing import Any

from app.mcp.builtin_tools import run_builtin_tool


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    """执行已注册工具。

    参数:
        tool_name: 工具名。
        arguments: 入参 dict。

    返回:
        Any: 执行结果。
    """
    return run_builtin_tool(tool_name, arguments)
