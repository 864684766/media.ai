"""save_messages 节点。

【职责】
    保存本轮 user / assistant 消息，并写入 state.message_ids。

【无数据库场景】
    未注入 repository 时返回 memory:* 占位，保证本地无 PG 也能测试。
"""

from app.graph.graph_constants import (
    MEMORY_MESSAGE_ID_ASSISTANT,
    MEMORY_MESSAGE_ID_USER,
)
from app.graph.message_persistence_helper import save_state_messages
from app.schemas.agent_state import AgentState
from app.storage.postgres.conversation_repository import ConversationRepository


def save_messages_node(
    state: AgentState,
    repository: ConversationRepository | None = None,
) -> AgentState:
    """保存本轮 user/assistant 消息。

    参数:
        state: 当前图状态。
        repository: 可选会话 Repository。

    返回:
        AgentState: 写入 message_ids 后的新状态。
    """
    if repository is not None:
        message_ids = save_state_messages(state, repository)
        return state.model_copy(update={"message_ids": message_ids})
    message_ids = [MEMORY_MESSAGE_ID_USER, MEMORY_MESSAGE_ID_ASSISTANT]
    return state.model_copy(update={"message_ids": message_ids})
