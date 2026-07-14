"""BGM 产物路径辅助（V8.6）。"""

from pathlib import Path

from app.core.bgm_constants import BGM_STORAGE_SEGMENT
from app.video.video_assets_config_reader import load_video_assets_config


def bgm_storage_dir(project_id: str) -> Path:
    """BGM 目录绝对路径。"""
    root = Path(load_video_assets_config().assets_dir)
    return root / project_id / BGM_STORAGE_SEGMENT


def bgm_relative_uri(project_id: str, filename: str) -> str:
    """BGM files API 相对路径。"""
    return f"{project_id}/{BGM_STORAGE_SEGMENT}/{filename}"


def bgm_absolute_path(project_id: str, filename: str) -> Path:
    """BGM 文件绝对路径。"""
    return bgm_storage_dir(project_id) / filename
