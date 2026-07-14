"""内置 MCP 工具目录（元数据）。"""

from app.mcp.mcp_video_tool_constants import (
    MCP_TOOL_COMPOSE_TIMELINE,
    MCP_TOOL_CONTINUITY_CHECK,
    MCP_TOOL_RENDER_SHOT,
)


def list_all_builtin_tool_meta() -> list[dict[str, str]]:
    """返回全部内置工具元数据。"""
    return [
        {"name": "echo", "description": "回显参数，用于连通性测试"},
        {"name": "list_project_docs", "description": "列出项目文档 id（占位）"},
        {
            "name": MCP_TOOL_RENDER_SHOT,
            "description": "渲染单镜切片，返回 clip_uri / keyframe_uri（阶段 D2）",
        },
        {
            "name": MCP_TOOL_CONTINUITY_CHECK,
            "description": "单镜连续性 QA，返回 pass 与 reasons（阶段 D2）",
        },
        {
            "name": MCP_TOOL_COMPOSE_TIMELINE,
            "description": "合成 qa_passed 镜头为 timeline 成片（阶段 D2）",
        },
    ]
