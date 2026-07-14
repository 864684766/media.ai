"""MCP render_shot 工具处理器。"""

from typing import Any

from app.mcp.mcp_video_tool_constants import ARG_SHOT_ID
from app.services.mcp_single_shot_render_service import render_single_shot_for_mcp
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


def handle_render_shot_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    """执行 render_shot MCP 工具。

    参数:
        arguments: 须含 shot_id。

    返回:
        dict: clip_uri 等出参。
    """
    shot_id = str(arguments.get(ARG_SHOT_ID, "")).strip()
    if not shot_id:
        raise ValueError("render_shot 需要 shot_id")
    if not is_postgres_configured():
        raise RuntimeError("未配置 DATABASE_URL")
    with postgres_session_scope() as session:
        return render_single_shot_for_mcp(session, shot_id)
