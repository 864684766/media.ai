"""Chat SSE runner 测试。"""

from app.schemas.chat import ChatRequest
from app.services.chat import ChatService


class BrokenRepository:
    """测试用坏 Repository：读取历史时抛错。"""

    def list_messages(self, conversation_id: str, retention_days: int | None = None) -> list:
        """模拟数据库读取失败。"""
        raise RuntimeError("模拟数据库错误")


def test_stream_chat_returns_error_event_on_exception() -> None:
    """图执行失败时应返回 status + error SSE，而不是抛出到接口外。"""
    service = ChatService(repository=BrokenRepository())  # type: ignore[arg-type]
    frames = list(service.stream_chat(ChatRequest(message="你好")))
    assert len(frames) >= 2
    assert any(f.startswith("event: status") for f in frames)
    error_frames = [f for f in frames if f.startswith("event: error")]
    assert len(error_frames) == 1
    assert "模拟数据库错误" in error_frames[0]
