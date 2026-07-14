"""MCP compose_timeline 工具处理器。"""

from typing import Any

from app.mcp.mcp_video_tool_constants import ARG_PROJECT_ID
from app.services.mcp_compose_timeline_service import compose_timeline_for_mcp
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


def handle_compose_timeline_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    """执行 compose_timeline MCP 工具。

    参数:
        arguments: 须含 project_id。

    返回:
        dict: output_uri 等出参。
    """
    project_id = str(arguments.get(ARG_PROJECT_ID, "")).strip()
    if not project_id:
        raise ValueError("compose_timeline 需要 project_id")
    if not is_postgres_configured():
        raise RuntimeError("未配置 DATABASE_URL")
    with postgres_session_scope() as session:
        return compose_timeline_for_mcp(session, project_id)
