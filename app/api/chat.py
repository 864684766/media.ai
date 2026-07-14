"""Chat 路由。

【职责】
    POST 提供 SSE 流式 Chat 接口（创作工作台唯一对话入口）。
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_chat_service
from app.core.constants import CHAT_ROUTE_PREFIX, SSE_MEDIA_TYPE
from app.schemas.chat import ChatRequest
from app.services.chat import ChatService

router = APIRouter(prefix=CHAT_ROUTE_PREFIX, tags=["chat"])


@router.post("", summary="Chat SSE 问答")
def post_chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """Chat SSE 端点。

    参数:
        request: 用户本轮输入与可选会话参数。
        service: ChatService 实例。

    返回:
        StreamingResponse: text/event-stream 事件流。
    """
    return StreamingResponse(
        service.stream_chat(request),
        media_type=SSE_MEDIA_TYPE,
    )
