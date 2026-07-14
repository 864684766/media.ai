"""MCP 视频工具分发器。"""

from typing import Any

from app.mcp.handlers.compose_timeline_tool_handler import handle_compose_timeline_tool
from app.mcp.handlers.continuity_check_tool_handler import handle_continuity_check_tool
from app.mcp.handlers.render_shot_tool_handler import handle_render_shot_tool
from app.mcp.mcp_video_tool_constants import (
    MCP_TOOL_COMPOSE_TIMELINE,
    MCP_TOOL_CONTINUITY_CHECK,
    MCP_TOOL_RENDER_SHOT,
)

_VIDEO_HANDLERS = {
    MCP_TOOL_RENDER_SHOT: handle_render_shot_tool,
    MCP_TOOL_CONTINUITY_CHECK: handle_continuity_check_tool,
    MCP_TOOL_COMPOSE_TIMELINE: handle_compose_timeline_tool,
}


def is_video_mcp_tool(tool_name: str) -> bool:
    """判断是否为视频生产线 MCP 工具。"""
    return tool_name in _VIDEO_HANDLERS


def dispatch_video_mcp_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    """分发并执行视频 MCP 工具。"""
    handler = _VIDEO_HANDLERS.get(tool_name)
    if handler is None:
        raise ValueError(f"未知视频 MCP 工具: {tool_name}")
    return handler(arguments)
