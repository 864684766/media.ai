"""分镜 JSON 解析测试。"""

import pytest

from app.video.storyboard_json_parser import parse_storyboard_json_array

_SAMPLE = [
    {
        "shot_no": "1",
        "duration_sec": 2,
        "action": "山门远景",
    },
]


def test_parse_raw_json_array() -> None:
    """纯 JSON 数组应直接解析。"""
    text = '[{"shot_no": "1", "duration_sec": 2, "action": "山门远景"}]'
    rows = parse_storyboard_json_array(text)
    assert rows[0]["shot_no"] == "1"


def test_parse_markdown_fence() -> None:
    """Markdown 代码块内的 JSON 应被提取。"""
    text = '说明\n```json\n[{"shot_no": "1", "duration_sec": 2, "action": "山门远景"}]\n```\n'
    rows = parse_storyboard_json_array(text)
    assert len(rows) == 1


def test_parse_invalid_raises() -> None:
    """无 JSON 数组时应抛 ValueError。"""
    with pytest.raises(ValueError):
        parse_storyboard_json_array("只有文字没有 JSON")
