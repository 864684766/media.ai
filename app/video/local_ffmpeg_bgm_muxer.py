"""BGM 混轨执行器（V8.6）。"""

import subprocess
from pathlib import Path


def mix_bgm_into_video(
    binary: str,
    video_path: Path,
    bgm_path: Path,
    output_path: Path,
    bgm_volume: float,
) -> None:
    """将 BGM 混入已有对白的 mp4。

    参数:
        binary: ffmpeg 路径。
        video_path: 已含对白音轨的 mp4。
        bgm_path: BGM 音频文件。
        output_path: 输出 mp4。
        bgm_volume: BGM 音量 0.0–1.0。

    异常:
        RuntimeError: ffmpeg 失败。
    """
    cmd = _build_mix_cmd(binary, video_path, bgm_path, output_path, bgm_volume)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "ffmpeg bgm mix failed")


def _build_mix_cmd(
    binary: str,
    video_path: Path,
    bgm_path: Path,
    output_path: Path,
    bgm_volume: float,
) -> list[str]:
    """构造 BGM amix 命令行。"""
    volume = max(0.0, min(float(bgm_volume), 1.0))
    filter_expr = f"[1:a]volume={volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]"
    return [
        binary,
        "-y",
        "-i",
        str(video_path),
        "-stream_loop",
        "-1",
        "-i",
        str(bgm_path),
        "-filter_complex",
        filter_expr,
        "-map",
        "0:v:0",
        "-map",
        "[aout]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        str(output_path),
    ]
