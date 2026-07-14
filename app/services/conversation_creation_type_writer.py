"""会话 creation_type 写入辅助。"""

from sqlalchemy.orm import Session

from app.core.creation_type_constants import ALLOWED_CREATION_TYPES
from app.storage.postgres.conversation_repository import ConversationRepository


def ensure_conversation_creation_type(
    repository: ConversationRepository,
    conversation_id: str,
    creation_type: str | None,
) -> None:
    """会话存在且 creation_type 为空时写入。

    参数:
        repository: 会话 Repository。
        conversation_id: 会话 id。
        creation_type: 本轮 Chat 请求的创作类型。
    """
    if not creation_type or creation_type not in ALLOWED_CREATION_TYPES:
        return
    row = repository.get_conversation(conversation_id)
    if row is None or row.creation_type:
        return
    repository.set_creation_type(conversation_id, creation_type)


def bind_conversation_creation_type(
    session: Session,
    conversation_id: str,
    project_id: str | None,
    creation_type: str | None,
) -> None:
    """创建或补全会话的 creation_type（澄清/首条消息前）。"""
    if not creation_type or creation_type not in ALLOWED_CREATION_TYPES:
        return
    repo = ConversationRepository(session)
    if repo.get_conversation(conversation_id) is None:
        repo.create_conversation(conversation_id, project_id, creation_type)
        return
    ensure_conversation_creation_type(repo, conversation_id, creation_type)
