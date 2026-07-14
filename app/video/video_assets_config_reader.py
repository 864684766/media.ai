"""视频资产目录配置读取。"""

from dataclasses import dataclass

from app.core.config_yaml_loader import load_app_yaml
from app.storage.postgres.postgres_constants import DEFAULT_VIDEO_ASSETS_DIR

YAML_KEY_VIDEO = "video"
YAML_KEY_ASSETS_DIR = "assets_dir"


@dataclass(frozen=True)
class VideoAssetsConfig:
    """视频资产落盘配置。"""

    assets_dir: str


def load_video_assets_config() -> VideoAssetsConfig:
    """读取 video.assets_dir。"""
    root = load_app_yaml()
    block = root.get(YAML_KEY_VIDEO, {})
    assets_dir = DEFAULT_VIDEO_ASSETS_DIR
    if isinstance(block, dict):
        assets_dir = str(block.get(YAML_KEY_ASSETS_DIR, assets_dir))
    return VideoAssetsConfig(assets_dir=assets_dir)
