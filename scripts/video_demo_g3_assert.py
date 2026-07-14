"""视频 E2E 演示 G3 字幕烧录断言。"""


def assert_subtitles_burned_field(compose_payload: dict) -> dict:
    """检查 compose 或 pipeline 响应是否含 subtitles_burned 字段。

    参数:
        compose_payload: compose 步骤或 pipeline compose_output 片段。

    返回:
        dict: 断言结果摘要。
    """
    burned = _resolve_burned_flag(compose_payload)
    return {
        "has_subtitles_burned_field": "subtitles_burned" in _flatten_keys(compose_payload),
        "subtitles_burned": burned,
    }


def _resolve_burned_flag(payload: dict) -> bool | None:
    """从嵌套结构读取 subtitles_burned。"""
    if "subtitles_burned" in payload:
        return bool(payload["subtitles_burned"])
    output = payload.get("output") or payload.get("compose_output")
    if isinstance(output, dict) and "subtitles_burned" in output:
        return bool(output["subtitles_burned"])
    return None


def _flatten_keys(payload: dict) -> set[str]:
    """收集顶层与 output 层键名。"""
    keys = set(payload.keys())
    output = payload.get("output") or payload.get("compose_output")
    if isinstance(output, dict):
        keys.update(output.keys())
    return keys
