"""Chat 接口测试。"""

from fastapi.testclient import TestClient

from app.application import app
from app.core.config import settings
from app.core.constants import CHAT_ROUTE_PREFIX, DEFAULT_CHAT_REPLY

client = TestClient(app)


def test_chat_endpoint() -> None:
    """验证 /chat 端点返回简单字符串。

    断言:
        - HTTP 状态码为 200
        - 响应体为默认 chat 应答文本
    """
    url = _build_chat_url()
    response = client.get(url)
    assert response.status_code == 200
    assert response.text == DEFAULT_CHAT_REPLY


def _build_chat_url() -> str:
    """构造 chat 接口完整路径。

    返回:
        str: 带 API 前缀的 chat 路径。
    """
    return f"{settings.api_prefix}{CHAT_ROUTE_PREFIX}"
