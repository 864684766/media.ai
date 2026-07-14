"""会话列表服务辅助。

【职责】
    组装 GET /conversations 的响应数据（ORM → Pydantic）。
"""

from sqlalchemy.orm import Session

from app.api.api_constants import DEFAULT_CONVERSATION_LIST_LIMIT
from app.schemas.conversation import ConversationListResponse, ConversationSummary
from app.storage.postgres.conversation_list_query import list_conversations_ordered
from app.storage.postgres.message_preview_helper import fetch_last_message_preview
from app.services.conversation_creation_type_resolver import resolve_conversation_creation_type


def build_conversation_list_response(
    session: Session,
    limit: int = DEFAULT_CONVERSATION_LIST_LIMIT,
) -> ConversationListResponse:
    """构建会话列表响应。

    参数:
        session: SQLAlchemy Session。
        limit: 最多返回条数。

    返回:
        ConversationListResponse: 含 preview 的会话列表。
    """
    rows = list_conversations_ordered(session, limit)
    items = [_to_summary(session, row) for row in rows]
    return ConversationListResponse(items=items)


def _to_summary(session: Session, row) -> ConversationSummary:
    """单条 ORM 转 ConversationSummary。"""
    preview = fetch_last_message_preview(session, row.id)
    creation_type = resolve_conversation_creation_type(session, row.id)
    return ConversationSummary(
        id=row.id,
        project_id=row.project_id,
        creation_type=creation_type,
        preview=preview,
        updated_at=row.updated_at,
    )
