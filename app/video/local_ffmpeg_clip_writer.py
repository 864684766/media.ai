"""local_ffmpeg 单镜 mp4 写入（V7）。

【职责】
    用 lavfi 色块 + drawtext 生成占位 mp4 切片（无需外网 API）。

【何时调用】
    clip_render_dispatcher 在 active.clip=local_ffmpeg 且 ffmpeg 可用时。
"""

import subprocess

from app.models.postgres.shot_model import ShotModel
from app.video.ffmpeg_binary_resolver import resolve_ffmpeg_binary
from app.video.video_asset_path_helper import clip_mp4_file_path


def write_local_ffmpeg_clip(shot: ShotModel) -> str:
    """写出 clip.mp4 并返回相对 URI。

    参数:
        shot: 镜头 ORM。

    返回:
        str: files API 相对路径。

    异常:
        RuntimeError: ffmpeg 不可用或执行失败。
    """
    binary = resolve_ffmpeg_binary()
    if binary is None:
        raise RuntimeError("ffmpeg not available")
    path = clip_mp4_file_path(shot.project_id, shot.shot_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    duration = max(float(shot.duration_sec or 1), 0.5)
    label = (shot.action or shot.shot_no).replace(":", " ").replace("'", "")
    _run_ffmpeg(binary, path, duration, label)
    return _relative_uri(shot.project_id, shot.shot_id, path.name)


def _relative_uri(project_id: str, shot_id: str, filename: str) -> str:
    """拼接相对 URI。"""
    return f"{project_id}/{shot_id}/{filename}"


def _run_ffmpeg(binary: str, path, duration: float, label: str) -> None:
    """调用 ffmpeg 生成 mp4。"""
    vf = f"drawtext=text='Shot {label}':fontsize=20:fontcolor=white:x=32:y=48"
    cmd = [
        binary, "-y", "-f", "lavfi",
        "-i", "color=c=#2563eb:s=640x360",
        "-vf", vf, "-t", str(duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "ffmpeg failed")
