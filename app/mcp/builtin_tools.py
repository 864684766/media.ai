"""内置 MCP 工具（Phase 3 本地实现，无需外部 Server）。"""

from typing import Any

from app.mcp.builtin_tool_catalog import list_all_builtin_tool_meta
from app.mcp.video_tool_dispatcher import dispatch_video_mcp_tool, is_video_mcp_tool


def list_builtin_tools() -> list[dict[str, str]]:
    """返回内置工具元数据列表。"""
    return list_all_builtin_tool_meta()


def run_builtin_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    """执行内置工具。

    参数:
        tool_name: 工具名。
        arguments: 入参。

    返回:
        Any: 工具结果。

    异常:
        ValueError: 未知工具名。
    """
    if is_video_mcp_tool(tool_name):
        return dispatch_video_mcp_tool(tool_name, arguments)
    if tool_name == "echo":
        return {"echo": arguments}
    if tool_name == "list_project_docs":
        return {"project_id": arguments.get("project_id", ""), "documents": []}
    raise ValueError(f"未知内置工具: {tool_name}")
