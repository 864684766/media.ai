"""历史 token 估算辅助。"""

from app.schemas.agent_state import ChatHistoryMessage


def estimate_history_tokens(messages: list[ChatHistoryMessage]) -> int:
    """用字符数近似 token 数。

    参数:
        messages: 历史消息列表。

    返回:
        int: 估算 token 数。
    """
    return sum(len(item.role) + len(item.content) for item in messages)
