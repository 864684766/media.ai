"""会话列表查询辅助。

【职责】
    从 conversations 表按更新时间倒序查询，供 GET /conversations 使用。
    与 ConversationRepository 分离，保持 Repository 单一职责。
"""

from sqlalchemy.orm import Session

from app.models.postgres.conversation_model import ConversationModel


def list_conversations_ordered(
    session: Session,
    limit: int,
) -> list[ConversationModel]:
    """按 updated_at 倒序返回会话列表。

    参数:
        session: SQLAlchemy Session。
        limit: 最多返回条数。

    返回:
        list[ConversationModel]: 会话 ORM 列表。
    """
    query = session.query(ConversationModel)
    return query.order_by(ConversationModel.updated_at.desc()).limit(limit).all()
