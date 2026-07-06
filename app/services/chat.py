"""Chat 业务服务。"""

from app.services.chat_helper import build_chat_reply


class ChatService:
    """Chat 业务服务，负责生成 chat 应答文本。"""

    def respond(self) -> str:
        """生成 chat 应答。

        返回:
            str: 简单字符串应答。
        """
        return build_chat_reply()
