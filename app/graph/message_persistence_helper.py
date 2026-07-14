"""消息持久化辅助。

【职责】
    封装 save_messages 节点的 Repository 写入细节。
"""

from app.services.conversation_creation_type_writer import ensure_conversation_creation_type
from app.services.message_artifact_service import save_assistant_txt_artifact
from app.storage.postgres import postgres_constants as pc
from app.storage.postgres.conversation_repository import ConversationRepository


def save_state_messages(
    state: AgentState,
    repository: ConversationRepository,
) -> list[str]:
    """保存本轮 user / assistant 消息。

    参数:
        state: 当前图状态。
        repository: 会话 Repository。

    返回:
        list[str]: 已保存消息 id。
    """
    ensure_conversation_exists(state, repository)
    user_message = repository.append_message(
        state.conversation_id,
        pc.MESSAGE_ROLE_USER,
        state.question,
    )
    assistant_message = repository.append_message(
        state.conversation_id,
        pc.MESSAGE_ROLE_ASSISTANT,
        state.answer,
    )
    save_assistant_txt_artifact(
        repository,
        state.conversation_id,
        assistant_message.id,
    )
    return [str(user_message.id), str(assistant_message.id)]


def ensure_conversation_exists(
    state: AgentState,
    repository: ConversationRepository,
) -> None:
    """若会话不存在则创建。"""
    if repository.get_conversation(state.conversation_id) is None:
        repository.create_conversation(
            state.conversation_id,
            state.project_id,
            state.creation_type,
        )
        return
    ensure_conversation_creation_type(
        repository,
        state.conversation_id,
        state.creation_type,
    )
