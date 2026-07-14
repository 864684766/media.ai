"""MCP 视频工具测试（阶段 D2）。"""

from app.mcp.builtin_tools import list_builtin_tools, run_builtin_tool
from app.mcp.mcp_video_tool_constants import (
    MCP_TOOL_COMPOSE_TIMELINE,
    MCP_TOOL_CONTINUITY_CHECK,
    MCP_TOOL_RENDER_SHOT,
)


def test_builtin_tools_include_video_mcp() -> None:
    """内置工具列表应含视频生产线三件套。"""
    names = {item["name"] for item in list_builtin_tools()}
    assert MCP_TOOL_RENDER_SHOT in names
    assert MCP_TOOL_CONTINUITY_CHECK in names
    assert MCP_TOOL_COMPOSE_TIMELINE in names


def test_render_shot_requires_shot_id() -> None:
    """render_shot 缺 shot_id 应报错。"""
    try:
        run_builtin_tool(MCP_TOOL_RENDER_SHOT, {})
        raised = False
    except ValueError as exc:
        raised = True
        assert "shot_id" in str(exc)
    assert raised


def test_compose_timeline_requires_project_id() -> None:
    """compose_timeline 缺 project_id 应报错。"""
    try:
        run_builtin_tool(MCP_TOOL_COMPOSE_TIMELINE, {})
        raised = False
    except ValueError as exc:
        raised = True
        assert "project_id" in str(exc)
    assert raised
