"""OpenAI 兼容 SSE 流解析测试。"""

from app.providers.openai_stream_parser import parse_openai_stream_chunk, parse_openai_stream_line


def test_parse_openai_stream_delta_line() -> None:
    """应从 data 行提取 delta.content。"""
    line = 'data: {"choices":[{"delta":{"content":"你"}}]}'
    assert parse_openai_stream_line(line) == "你"


def test_parse_openai_stream_done_line() -> None:
    """[DONE] 行不产生文本。"""
    assert parse_openai_stream_line("data: [DONE]") is None


def test_parse_openai_stream_empty_line() -> None:
    """空行或非 data 行不产生文本。"""
    assert parse_openai_stream_line("") is None


def test_parse_openai_stream_usage_chunk() -> None:
    """应能解析 usage 统计。"""
    line = 'data: {"choices":[],"usage":{"total_tokens":3}}'
    chunk = parse_openai_stream_chunk(line)
    assert chunk is not None
    assert chunk.usage == {"total_tokens": 3}
