"""load_history 节点。

【职责】
    从 ConversationRepository 读取历史消息，并写入 state.history。
    只加载 history.retention_days（config/app.yaml）保留期内的消息，
    对应 sec-14.3「原始消息保留」策略。

【无数据库场景】
    未注入 repository 时保持空 history，便于本地无 PG 也能跑通接口。
"""

from app.graph.history_message_converter import to_history_message
from app.schemas.agent_state import AgentState
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.history_settings_reader import load_history_retention_days


def load_history_node(
    state: AgentState,
    repository: ConversationRepository | None = None,
) -> AgentState:
    """加载保留期内的历史消息。

    参数:
        state: 当前图状态。
        repository: 可选会话 Repository。

    返回:
        AgentState: 写入 history 后的新状态。
    """
    if repository is None:
        return state
    retention_days = load_history_retention_days()
    messages = repository.list_messages(state.conversation_id, retention_days=retention_days)
    history = [to_history_message(message) for message in messages]
    return state.model_copy(update={"history": history})
