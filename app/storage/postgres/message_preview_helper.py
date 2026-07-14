"""会话最近消息摘要辅助。

【职责】
    为会话列表项生成 preview 字段（取该会话最后一条消息的前 N 个字符）。
"""

from sqlalchemy.orm import Session

from app.models.postgres.message_model import MessageModel

# 列表预览最大字符数（超出截断并加省略号）
PREVIEW_MAX_CHARS = 80
PREVIEW_ELLIPSIS = "…"


def fetch_last_message_preview(
    session: Session,
    conversation_id: str,
) -> str:
    """获取会话最近一条消息的摘要文本。

    参数:
        session: SQLAlchemy Session。
        conversation_id: 会话 id。

    返回:
        str: 摘要；无消息时返回空字符串。
    """
    message = _query_last_message(session, conversation_id)
    if message is None:
        return ""
    return _clip_preview(message.content)


def _query_last_message(
    session: Session,
    conversation_id: str,
) -> MessageModel | None:
    """查询会话最后一条消息。"""
    query = session.query(MessageModel)
    query = query.filter(MessageModel.conversation_id == conversation_id)
    return query.order_by(MessageModel.id.desc()).first()


def _clip_preview(content: str) -> str:
    """截断预览文本。"""
    if len(content) <= PREVIEW_MAX_CHARS:
        return content
    return content[:PREVIEW_MAX_CHARS] + PREVIEW_ELLIPSIS
