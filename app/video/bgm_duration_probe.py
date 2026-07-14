"""BGM 音频时长探测（ffprobe）。"""

import subprocess
from pathlib import Path

from app.video.ffmpeg_binary_resolver import resolve_ffmpeg_binary


def probe_audio_duration_sec(path: Path) -> float:
    """用 ffprobe 读取音频时长。

    参数:
        path: 音频文件绝对路径。

    返回:
        float: 时长秒；失败时 0.0。
    """
    binary = resolve_ffmpeg_binary()
    if binary is None or not path.is_file():
        return 0.0
    ffprobe = _ffprobe_path(binary)
    cmd = [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return 0.0
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def _ffprobe_path(ffmpeg_binary: str) -> str:
    """由 ffmpeg 路径推断 ffprobe。"""
    if ffmpeg_binary.lower().endswith("ffmpeg.exe"):
        return ffmpeg_binary[:-10] + "ffprobe.exe"
    if ffmpeg_binary.endswith("ffmpeg"):
        return ffmpeg_binary.replace("ffmpeg", "ffprobe")
    return "ffprobe"
