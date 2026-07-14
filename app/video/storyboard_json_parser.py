"""分镜 JSON 解析辅助。

【职责】
    从 LLM 回复或 CLI 文件内容中提取 Shot JSON 数组（容忍 Markdown 代码块包裹）。

【何时调用】
    submit_storyboard CLI、后续从 chat 回复自动入库（V2+）时复用。

【简例】
    shots = parse_storyboard_json_array(text)  # → list[dict]
"""

import json
import re

# Markdown 围栏内 JSON 数组
_JSON_FENCE_PATTERN = re.compile(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", re.IGNORECASE)


def _loads_array(raw: str) -> list[dict]:
    """将 JSON 文本解析为对象数组。

    参数:
        raw: JSON 数组字符串。

    返回:
        list[dict]: 解析后的字典列表。

    异常:
        ValueError: 非数组或元素非对象时抛出。
    """
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        raise ValueError("分镜 JSON 必须是数组")
    rows: list[dict] = []
    for item in parsed:
        if not isinstance(item, dict):
            raise ValueError("分镜数组元素必须是对象")
        rows.append(item)
    return rows


def parse_storyboard_json_array(text: str) -> list[dict]:
    """从纯 JSON 或 Markdown 代码块中解析分镜数组。

    参数:
        text: 文件或 LLM 回复全文。

    返回:
        list[dict]: Shot 字典列表。

    异常:
        ValueError: 找不到合法 JSON 数组时抛出。
    """
    stripped = text.strip()
    if not stripped:
        raise ValueError("分镜内容为空")
    fence = _JSON_FENCE_PATTERN.search(stripped)
    if fence:
        return _loads_array(fence.group(1))
    if stripped.startswith("["):
        return _loads_array(stripped)
    raise ValueError("未找到分镜 JSON 数组（可用 ```json [...] ``` 包裹）")
