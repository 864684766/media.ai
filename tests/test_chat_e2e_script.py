"""run_chat_e2e 脚本辅助函数测试。"""

from scripts.run_chat_e2e import _extract_conversation_id


def test_extract_conversation_id_from_sse_text() -> None:
    """应能从 message_start data 行中提取 conversation_id。"""
    sse_text = 'event: message_start\ndata: {"conversation_id": "c-1"}\n\n'
    assert _extract_conversation_id(sse_text) == "c-1"
