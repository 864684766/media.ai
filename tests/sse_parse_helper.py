"""SSE 测试解析辅助（tests 共用）。"""

import json

from app.core import constants


def parse_sse_events(raw: str) -> list[tuple[str, dict]]:
    """解析 SSE 文本为 (event_name, data) 列表。

    参数:
        raw: SSE 响应全文。

    返回:
        list[tuple[str, dict]]: 事件名与 data 字典。
    """
    events: list[tuple[str, dict]] = []
    for block in raw.split("\n\n"):
        if not block.strip():
            continue
        event_name = ""
        data_text = ""
        for line in block.split("\n"):
            if line.startswith("event: "):
                event_name = line[7:].strip()
            if line.startswith("data: "):
                data_text = line[6:]
        if event_name and data_text:
            events.append((event_name, json.loads(data_text)))
    return events


def extract_conversation_id(raw: str) -> str:
    """从 SSE 流中提取 conversation_id（message_start 事件）。

    参数:
        raw: SSE 响应全文。

    返回:
        str: conversation_id。

    异常:
        KeyError: 未找到 message_start 或 conversation_id 字段。
    """
    for event_name, data in parse_sse_events(raw):
        if event_name == constants.SSE_EVENT_MESSAGE_START:
            return str(data[constants.SSE_FIELD_CONVERSATION_ID])
    raise KeyError("conversation_id not found in SSE stream")


def extract_event_names(raw: str) -> list[str]:
    """提取 SSE 事件名序列（断言契约用）。

    参数:
        raw: SSE 响应全文。

    返回:
        list[str]: 按出现顺序的事件名列表。
    """
    return [name for name, _ in parse_sse_events(raw)]
