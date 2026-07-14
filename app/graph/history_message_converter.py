"""历史消息转换辅助。

【职责】
    将数据库 MessageModel 转为图内 ChatHistoryMessage。
"""

from typing import Protocol

from app.schemas.agent_state import ChatHistoryMessage


class MessageLike(Protocol):
    """MessageModel 需要具备的最小字段协议。"""

    role: str
    content: str


def to_history_message(message: MessageLike) -> ChatHistoryMessage:
    """将数据库消息对象转为图内历史消息。

    参数:
        message: 具备 role/content 字段的消息对象。

    返回:
        ChatHistoryMessage: 图内 history 项。
    """
    return ChatHistoryMessage(role=message.role, content=message.content)
