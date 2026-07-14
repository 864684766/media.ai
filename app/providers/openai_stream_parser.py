"""OpenAI 兼容 SSE 流解析器。

【职责】
    从 Provider 返回的 SSE 行中提取 choices[0].delta.content。

【输入示例】
    data: {"choices":[{"delta":{"content":"你"}}]}
    data: [DONE]

【输出示例】
    "你"
"""

import json
from typing import Any

from app.providers import provider_constants as pc
from app.providers.provider_stream_models import ProviderStreamChunk


def parse_openai_stream_line(line: str) -> str | None:
    """解析单行 OpenAI 兼容 SSE。

    参数:
        line: httpx.iter_lines() 返回的一行文本。

    返回:
        str | None: 有内容则返回 delta 文本；空行、DONE 或无内容返回 None。
    """
    chunk = parse_openai_stream_chunk(line)
    return chunk.delta if chunk is not None else None


def parse_openai_stream_chunk(line: str) -> ProviderStreamChunk | None:
    """解析单行 OpenAI 兼容 SSE 为结构化 chunk。

    参数:
        line: httpx.iter_lines() 返回的一行文本。

    返回:
        ProviderStreamChunk | None: 空行或 DONE 返回 None。
    """
    if not _is_data_line(line):
        return None
    payload = _strip_data_prefix(line)
    if payload == pc.OPENAI_SSE_DONE_MARKER:
        return None
    return _extract_stream_chunk(payload)


def _is_data_line(line: str) -> bool:
    """判断是否为 SSE data 行。"""
    return line.startswith(pc.OPENAI_SSE_DATA_PREFIX)


def _strip_data_prefix(line: str) -> str:
    """去掉 data: 前缀。"""
    return line.removeprefix(pc.OPENAI_SSE_DATA_PREFIX).strip()


def _extract_delta_content(payload: str) -> str | None:
    """从 JSON payload 提取 delta.content。"""
    data = json.loads(payload)
    delta = _read_first_delta(data)
    content = delta.get(pc.OPENAI_FIELD_CONTENT)
    return content if isinstance(content, str) and content else None


def _extract_stream_chunk(payload: str) -> ProviderStreamChunk:
    """从 JSON payload 提取 delta / usage。"""
    data = json.loads(payload)
    return ProviderStreamChunk(
        delta=_extract_delta_content(payload),
        usage=_read_usage(data),
    )


def _read_usage(data: dict[str, Any]) -> dict | None:
    """读取 usage 字典。"""
    usage = data.get(pc.OPENAI_FIELD_USAGE)
    return usage if isinstance(usage, dict) else None


def _read_first_delta(data: dict[str, Any]) -> dict[str, Any]:
    """读取 choices[0].delta 字典。"""
    choices = data.get(pc.OPENAI_FIELD_CHOICES, [])
    if not choices:
        return {}
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return {}
    delta = first_choice.get(pc.OPENAI_FIELD_DELTA, {})
    return delta if isinstance(delta, dict) else {}
