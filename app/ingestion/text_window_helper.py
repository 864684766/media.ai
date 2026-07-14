"""文本滑动窗口辅助。

【职责】
    按 chunk_size / overlap 计算文本切片窗口。
"""


def iter_text_windows(text: str, chunk_size: int, overlap: int) -> list[str]:
    """按滑动窗口切分文本。

    参数:
        text: 原始文本。
        chunk_size: 每块最大字符数。
        overlap: 相邻块重叠字符数。

    返回:
        list[str]: 非空文本块。
    """
    normalized = text.strip()
    if not normalized:
        return []
    step = _safe_step(chunk_size, overlap)
    return _collect_windows(normalized, chunk_size, step)


def _safe_step(chunk_size: int, overlap: int) -> int:
    """计算安全步长，避免 overlap >= chunk_size 时死循环。"""
    safe_overlap = min(max(0, overlap), chunk_size - 1)
    return chunk_size - safe_overlap


def _collect_windows(text: str, chunk_size: int, step: int) -> list[str]:
    """收集所有滑动窗口。"""
    windows: list[str] = []
    start = 0
    while start < len(text):
        windows.append(text[start : start + chunk_size].strip())
        start += step
    return [item for item in windows if item]
