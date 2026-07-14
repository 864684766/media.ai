"""ffmpeg 字幕烧录执行器（阶段 G3）。"""

import subprocess
from pathlib import Path

from app.core.subtitle_burn_constants import (
    SUBTITLE_BURN_CRF,
    SUBTITLE_BURN_PRESET,
    SUBTITLE_BURN_VIDEO_CODEC,
    SUBTITLE_FORCE_STYLE,
)
from app.video.subtitle_filter_path_escaper import escape_path_for_subtitles_filter


def burn_subtitles_into_mp4(
    binary: str,
    video_path: Path,
    srt_path: Path,
    output_path: Path,
) -> None:
    """将 SRT 硬字幕烧录进 mp4。

    参数:
        binary: ffmpeg 可执行路径。
        video_path: 输入 mp4。
        srt_path: 字幕 SRT。
        output_path: 输出 mp4。

    异常:
        RuntimeError: ffmpeg 失败。
    """
    cmd = _build_burn_cmd(binary, video_path, srt_path, output_path)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "ffmpeg subtitle burn failed")


def _build_burn_cmd(
    binary: str,
    video_path: Path,
    srt_path: Path,
    output_path: Path,
) -> list[str]:
    """构造字幕烧录命令行。"""
    escaped = escape_path_for_subtitles_filter(srt_path)
    vf = f"subtitles={escaped}:force_style='{SUBTITLE_FORCE_STYLE}'"
    return [
        binary,
        "-y",
        "-i",
        str(video_path),
        "-vf",
        vf,
        "-c:v",
        SUBTITLE_BURN_VIDEO_CODEC,
        "-preset",
        SUBTITLE_BURN_PRESET,
        "-crf",
        str(SUBTITLE_BURN_CRF),
        "-c:a",
        "copy",
        str(output_path),
    ]
