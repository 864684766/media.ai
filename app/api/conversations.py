"""会话读 API 路由。

【职责】
    GET /conversations：会话列表（供前端左侧栏）
    GET /conversations/{id}/messages：历史消息（切换会话时回显）
"""

from fastapi import APIRouter, Depends, HTTPException

from app.api.api_constants import CONVERSATIONS_ROUTE_PREFIX, DEFAULT_CONVERSATION_LIST_LIMIT
from app.api.deps import get_postgres_repository
from app.schemas.conversation import ConversationListResponse, MessageListResponse
from app.services.conversation_list_service import build_conversation_list_response
from app.services.conversation_messages_service import build_message_list_response
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=CONVERSATIONS_ROUTE_PREFIX, tags=["conversations"])


@router.get("", summary="会话列表")
def list_conversations(
    limit: int = DEFAULT_CONVERSATION_LIST_LIMIT,
) -> ConversationListResponse:
    """返回按更新时间倒序的会话列表。

    参数:
        limit: 最多返回条数。

    返回:
        ConversationListResponse: 会话摘要列表；未配置 PG 时为空列表。
    """
    if not is_postgres_configured():
        return ConversationListResponse(items=[])
    with postgres_session_scope() as session:
        return build_conversation_list_response(session, limit=limit)


@router.get("/{conversation_id}/messages", summary="会话历史消息")
def list_conversation_messages(
    conversation_id: str,
    repository: ConversationRepository | None = Depends(get_postgres_repository),
) -> MessageListResponse:
    """返回指定会话的历史消息（受 retention_days 过滤）。

    参数:
        conversation_id: 会话 id。
        repository: 可选 PG Repository。

    返回:
        MessageListResponse: 消息列表。

    异常:
        HTTPException: 404 会话不存在或未配置数据库。
    """
    if repository is None:
        raise HTTPException(status_code=404, detail="未配置数据库或会话不存在")
    response = build_message_list_response(repository, conversation_id)
    if response is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    return response
