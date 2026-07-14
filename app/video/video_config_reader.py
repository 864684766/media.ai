"""视频分镜运维配置读取。

【职责】
    从 config/app.yaml 的 video.storyboard 段读取 V1 行为开关。

【何时调用】
    storyboard_service 提交入库前读取 replace_on_submit / default_status。

【简例】
    cfg = load_video_storyboard_config()
    if cfg.replace_on_submit: repository.delete_by_project(...)
"""

from dataclasses import dataclass

from app.core.config_yaml_loader import load_app_yaml
from app.core.video_constants import DEFAULT_SHOT_STATUS
from app.video.video_config_constants import (
    DEFAULT_REPLACE_ON_SUBMIT,
    YAML_KEY_DEFAULT_STATUS,
    YAML_KEY_REPLACE_ON_SUBMIT,
    YAML_KEY_STORYBOARD,
    YAML_KEY_VIDEO,
)


@dataclass(frozen=True)
class VideoStoryboardConfig:
    """分镜入库配置。

    字段:
        replace_on_submit: 提交时是否删除同 project 旧镜头。
        default_status: 新镜头初始状态。
    """

    replace_on_submit: bool
    default_status: str


def _read_storyboard_dict() -> dict:
    """从 app.yaml 取出 video.storyboard 字典。

    返回:
        dict: 可能为空字典。
    """
    root = load_app_yaml()
    video_block = root.get(YAML_KEY_VIDEO, {})
    if not isinstance(video_block, dict):
        return {}
    storyboard = video_block.get(YAML_KEY_STORYBOARD, {})
    return storyboard if isinstance(storyboard, dict) else {}


def load_video_storyboard_config() -> VideoStoryboardConfig:
    """加载分镜入库配置（缺省走常量默认）。

    返回:
        VideoStoryboardConfig: 合并 app.yaml 与代码默认值后的配置。
    """
    block = _read_storyboard_dict()
    replace = block.get(YAML_KEY_REPLACE_ON_SUBMIT, DEFAULT_REPLACE_ON_SUBMIT)
    status = block.get(YAML_KEY_DEFAULT_STATUS, DEFAULT_SHOT_STATUS)
    return VideoStoryboardConfig(
        replace_on_submit=bool(replace),
        default_status=str(status),
    )
