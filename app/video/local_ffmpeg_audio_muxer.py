"""ffmpeg 音画混轨执行器（V8.5）。"""

import subprocess
from pathlib import Path


def mux_video_with_audio(binary: str, video_path: Path, audio_path: Path, output_path: Path) -> None:
    """将视频轨与对白 WAV 混为 mp4。

    参数:
        binary: ffmpeg 可执行路径。
        video_path: 拼接后的视频 mp4。
        audio_path: 时间轴对白 WAV。
        output_path: 最终 mp4 路径。

    异常:
        RuntimeError: ffmpeg 失败。
    """
    cmd = _build_mux_cmd(binary, video_path, audio_path, output_path)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "ffmpeg mux failed")


def _build_mux_cmd(binary: str, video_path: Path, audio_path: Path, output_path: Path) -> list[str]:
    """构造 ffmpeg mux 命令行。"""
    return [
        binary,
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        str(output_path),
    ]
