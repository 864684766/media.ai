"""ffmpeg subtitles 滤镜路径转义。"""

from pathlib import Path


def escape_path_for_subtitles_filter(path: Path) -> str:
    """将绝对路径转为 subtitles 滤镜可接受的转义串。

    参数:
        path: SRT 绝对路径。

    返回:
        str: 已加引号、转义冒号与反斜杠的路径片段。
    """
    posix = path.resolve().as_posix()
    escaped = posix.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    return f"'{escaped}'"
