"""视频资产路径辅助。"""

from pathlib import Path

from app.video.video_assets_config_reader import load_video_assets_config


def shot_asset_dir(project_id: str, shot_id: str) -> Path:
    """镜头资产目录路径。"""
    root = Path(load_video_assets_config().assets_dir)
    return root / project_id / shot_id


def keyframe_file_path(project_id: str, shot_id: str) -> Path:
    """关键帧 Stub 文件路径（SVG）。"""
    return shot_asset_dir(project_id, shot_id) / "keyframe.svg"


def clip_file_path(project_id: str, shot_id: str) -> Path:
    """切片 Stub 文件路径（可下载占位）。"""
    return shot_asset_dir(project_id, shot_id) / "clip.stub.txt"


def clip_mp4_file_path(project_id: str, shot_id: str) -> Path:
    """V7 local_ffmpeg 切片 mp4 路径。"""
    from app.core.video_constants import CLIP_FILENAME_MP4

    return shot_asset_dir(project_id, shot_id) / CLIP_FILENAME_MP4
