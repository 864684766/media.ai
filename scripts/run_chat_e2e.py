"""真实多轮 Chat E2E 脚本。

【用途】
    连续向 POST /api/v1/chat 发送两轮消息，验证 conversation_id 续聊链路。

【运行】
    poetry run python scripts/run_chat_e2e.py

【前置】
    1. 已配置 .env（Provider Key、DATABASE_URL 可选）
    2. 若要落库，先运行 scripts/init_postgres_tables.py
"""

import json

from fastapi.testclient import TestClient

from app.application import app
from app.core.config import settings
from app.core.constants import CHAT_ROUTE_PREFIX


def main() -> None:
    """执行两轮 Chat E2E。"""
    client = TestClient(app)
    first_text = _post_chat(client, "你好，请用一句话介绍你自己。")
    conversation_id = _extract_conversation_id(first_text)
    second_text = _post_chat(client, "继续上一轮，补充一句。", conversation_id)
    print("== first response ==")
    print(first_text)
    print("== second response ==")
    print(second_text)


def _post_chat(
    client: TestClient,
    message: str,
    conversation_id: str | None = None,
) -> str:
    """发送一轮 Chat 请求并返回 SSE 文本。"""
    payload = {"message": message, "stream": True}
    if conversation_id is not None:
        payload["conversation_id"] = conversation_id
    response = client.post(_chat_url(), json=payload)
    response.raise_for_status()
    return response.text


def _chat_url() -> str:
    """返回 Chat API 路径。"""
    return f"{settings.api_prefix}{CHAT_ROUTE_PREFIX}"


def _extract_conversation_id(sse_text: str) -> str:
    """从 message_start 事件里提取 conversation_id。"""
    for line in sse_text.splitlines():
        if line.startswith("data: "):
            data = json.loads(line.removeprefix("data: "))
            if "conversation_id" in data:
                return data["conversation_id"]
    raise RuntimeError("SSE 响应中未找到 conversation_id")


if __name__ == "__main__":
    main()
