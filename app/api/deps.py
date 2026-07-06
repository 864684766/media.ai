"""依赖注入辅助方法。

集中管理路由层使用的依赖工厂，便于测试时替换实现。
"""

from app.services.chat import ChatService


def get_chat_service() -> ChatService:
    """构造 ChatService 实例。

    返回:
        ChatService: 注入到路由的服务实例。
    """
    return ChatService()
