"""视频合成配置读取。"""

from dataclasses import dataclass

from app.core.config_yaml_loader import load_app_yaml
from app.core.video_constants import DEFAULT_COMPOSE_OUTPUT_FILENAME
from app.video.video_budget_constants import DEFAULT_COMPOSE_MP4_FILENAME
from app.video.video_config_constants import (
    YAML_KEY_COMPOSE,
    YAML_KEY_OUTPUT_FILENAME,
    YAML_KEY_OUTPUT_MP4_FILENAME,
    YAML_KEY_VIDEO,
)


@dataclass(frozen=True)
class VideoComposeConfig:
    """合成落盘配置。"""

    output_filename: str
    output_mp4_filename: str


def load_video_compose_config() -> VideoComposeConfig:
    """读取 video.compose 输出文件名。"""
    root = load_app_yaml()
    video_block = root.get(YAML_KEY_VIDEO, {})
    filename = DEFAULT_COMPOSE_OUTPUT_FILENAME
    mp4_name = DEFAULT_COMPOSE_MP4_FILENAME
    if isinstance(video_block, dict):
        compose_block = video_block.get(YAML_KEY_COMPOSE, {})
        if isinstance(compose_block, dict):
            filename = str(compose_block.get(YAML_KEY_OUTPUT_FILENAME, filename))
            mp4_name = str(compose_block.get(YAML_KEY_OUTPUT_MP4_FILENAME, mp4_name))
    return VideoComposeConfig(output_filename=filename, output_mp4_filename=mp4_name)
