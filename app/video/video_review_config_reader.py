"""HITL 审核配置读取。"""

from dataclasses import dataclass

from app.core.config_yaml_loader import load_app_yaml
from app.video.video_config_constants import (
    DEFAULT_REVIEW_KEYFRAME_ENABLED,
    DEFAULT_REVIEW_STORYBOARD_ENABLED,
    YAML_KEY_REVIEW,
    YAML_KEY_REVIEW_KEYFRAME,
    YAML_KEY_REVIEW_STORYBOARD,
    YAML_KEY_VIDEO,
)


@dataclass(frozen=True)
class VideoReviewConfig:
    """video.review 段配置。"""

    storyboard_enabled: bool
    keyframe_enabled: bool


def load_video_review_config() -> VideoReviewConfig:
    """读取 HITL 开关。"""
    root = load_app_yaml()
    storyboard = DEFAULT_REVIEW_STORYBOARD_ENABLED
    keyframe = DEFAULT_REVIEW_KEYFRAME_ENABLED
    video_block = root.get(YAML_KEY_VIDEO, {})
    if isinstance(video_block, dict):
        review_block = video_block.get(YAML_KEY_REVIEW, {})
        if isinstance(review_block, dict):
            storyboard = bool(
                review_block.get(YAML_KEY_REVIEW_STORYBOARD, storyboard),
            )
            keyframe = bool(
                review_block.get(YAML_KEY_REVIEW_KEYFRAME, keyframe),
            )
    return VideoReviewConfig(
        storyboard_enabled=storyboard,
        keyframe_enabled=keyframe,
    )
