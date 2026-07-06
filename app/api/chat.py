"""Chat 路由。

提供 chat 接口，返回简单字符串应答。
"""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.api.deps import get_chat_service
from app.core.constants import CHAT_ROUTE_PREFIX
from app.services.chat import ChatService

router = APIRouter(prefix=CHAT_ROUTE_PREFIX, tags=["chat"])


@router.get("", response_class=PlainTextResponse, summary="Chat 应答")
def chat(service: ChatService = Depends(get_chat_service)) -> str:
    """Chat 端点，返回简单字符串。

    参数:
        service: 通过依赖注入获取的 ChatService 实例。

    返回:
        str: 纯文本应答。
    """
    return service.respond()
