"""视频 QA 配置读取。"""

from dataclasses import dataclass

from app.core.config_yaml_loader import load_app_yaml
from app.video.video_config_constants import (
    DEFAULT_QA_MAX_RETRIES,
    YAML_KEY_MAX_RETRIES,
    YAML_KEY_QA,
    YAML_KEY_VIDEO,
)


@dataclass(frozen=True)
class VideoQaConfig:
    """连续性 QA 配置。"""

    max_retries: int


def load_video_qa_config() -> VideoQaConfig:
    """读取 video.qa.max_retries。"""
    root = load_app_yaml()
    video_block = root.get(YAML_KEY_VIDEO, {})
    max_retries = DEFAULT_QA_MAX_RETRIES
    if isinstance(video_block, dict):
        qa_block = video_block.get(YAML_KEY_QA, {})
        if isinstance(qa_block, dict):
            raw = qa_block.get(YAML_KEY_MAX_RETRIES, max_retries)
            max_retries = int(raw)
    return VideoQaConfig(max_retries=max_retries)
