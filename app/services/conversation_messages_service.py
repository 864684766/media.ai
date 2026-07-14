"""会话消息列表服务辅助。

【职责】
    组装 GET /conversations/{id}/messages 的响应数据。
"""

from app.models.postgres.message_model import MessageModel
from app.services.conversation_creation_type_resolver import resolve_conversation_creation_type
from app.schemas.conversation import MessageItem, MessageListResponse
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.history_settings_reader import load_history_retention_days


def build_message_list_response(
    repository: ConversationRepository,
    conversation_id: str,
) -> MessageListResponse | None:
    """构建消息列表响应；会话不存在时返回 None。

    参数:
        repository: 会话 Repository。
        conversation_id: 会话 id。

    返回:
        MessageListResponse | None: 会话存在时返回列表，否则 None。
    """
    if repository.get_conversation(conversation_id) is None:
        return None
    retention = load_history_retention_days()
    messages = repository.list_messages(conversation_id, retention_days=retention)
    items = [_to_item(message) for message in messages]
    creation_type = resolve_conversation_creation_type(
        repository.db_session,
        conversation_id,
    )
    return MessageListResponse(
        conversation_id=conversation_id,
        creation_type=creation_type,
        items=items,
    )


def _to_item(message: MessageModel) -> MessageItem:
    """ORM 消息转 API 项。"""
    return MessageItem(
        id=message.id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
    )
