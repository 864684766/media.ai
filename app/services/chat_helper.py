"""Chat 接口辅助方法。

将应答文本构造逻辑单独放置，保证 service 文件单一职责。
"""

from app.core.constants import DEFAULT_CHAT_REPLY


def build_chat_reply() -> str:
    """构造 chat 接口的默认应答文本。

    返回:
        str: 应答字符串。
    """
    return DEFAULT_CHAT_REPLY
