"""MCP continuity_check 工具处理器。"""

from typing import Any

from app.mcp.mcp_video_tool_constants import ARG_SHOT_ID
from app.services.mcp_shot_continuity_check_service import check_shot_continuity_for_mcp
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


def handle_continuity_check_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    """执行 continuity_check MCP 工具。

    参数:
        arguments: 须含 shot_id。

    返回:
        dict: pass 与 reasons。
    """
    shot_id = str(arguments.get(ARG_SHOT_ID, "")).strip()
    if not shot_id:
        raise ValueError("continuity_check 需要 shot_id")
    if not is_postgres_configured():
        raise RuntimeError("未配置 DATABASE_URL")
    with postgres_session_scope() as session:
        return check_shot_continuity_for_mcp(session, shot_id)
