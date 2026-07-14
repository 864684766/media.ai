"""合成产物路径辅助。"""

from pathlib import Path

from app.video.video_assets_config_reader import load_video_assets_config
from app.video.video_compose_config_reader import load_video_compose_config


def compose_output_path(project_id: str) -> Path:
    """成片 Stub 文件绝对路径。"""
    root = Path(load_video_assets_config().assets_dir)
    filename = load_video_compose_config().output_filename
    return root / project_id / "compose" / filename


def compose_output_relative_uri(project_id: str) -> str:
    """供 files API 使用的相对 URI（JSON Stub）。"""
    filename = load_video_compose_config().output_filename
    return f"{project_id}/compose/{filename}"


def compose_mp4_relative_uri(project_id: str) -> str:
    """V7 ffmpeg 成片 mp4 相对 URI。"""
    filename = load_video_compose_config().output_mp4_filename
    return f"{project_id}/compose/{filename}"
