"""字幕 SRT 生成（V8）。

【职责】
    按镜号顺序将 shots.dialogue 转为简易 SRT 条目。

【何时调用】
    audio_pipeline_service 落盘字幕。
"""

from app.models.postgres.shot_model import ShotModel


def build_srt_content(shots: list[ShotModel]) -> str:
    """生成 SRT 文本。

    参数:
        shots: 已排序镜头列表。

    返回:
        str: UTF-8 SRT 内容。
    """
    lines: list[str] = []
    cursor = 0.0
    index = 1
    for shot in shots:
        text = (shot.dialogue or "").strip()
        if not text:
            cursor += float(shot.duration_sec or 0)
            continue
        end = cursor + float(shot.duration_sec or 1.0)
        lines.extend(_entry_lines(index, cursor, end, text))
        index += 1
        cursor = end
    return "\n".join(lines) + ("\n" if lines else "")


def _entry_lines(index: int, start: float, end: float, text: str) -> list[str]:
    """单条 SRT 块。"""
    return [
        str(index),
        f"{_ts(start)} --> {_ts(end)}",
        text,
        "",
    ]


def _ts(seconds: float) -> str:
    """秒转 SRT 时间戳。"""
    total_ms = int(seconds * 1000)
    h = total_ms // 3600000
    m = (total_ms % 3600000) // 60000
    s = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
