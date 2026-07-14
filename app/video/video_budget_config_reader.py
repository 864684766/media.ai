"""视频预算配置读取（V7）。

【职责】
    从 app.yaml video.budget 读取限额与熔断开关。

【何时调用】
    render/compose Job 启动前由 project_budget_gate 读取。
"""

from dataclasses import dataclass

from app.core.config_yaml_loader import load_app_yaml
from app.video.video_budget_constants import (
    DEFAULT_BUDGET_LIMIT_USD,
    DEFAULT_FUSE_ON_COMPOSE,
    DEFAULT_FUSE_ON_RENDER,
    YAML_KEY_BUDGET,
    YAML_KEY_DEFAULT_LIMIT_USD,
    YAML_KEY_FUSE_ON_COMPOSE,
    YAML_KEY_FUSE_ON_RENDER,
)
from app.video.video_config_constants import YAML_KEY_VIDEO


@dataclass(frozen=True)
class VideoBudgetConfig:
    """项目预算熔断配置。"""

    default_limit_usd: float
    fuse_on_render: bool
    fuse_on_compose: bool


def _read_budget_dict() -> dict:
    """取出 video.budget 字典。"""
    root = load_app_yaml()
    video = root.get(YAML_KEY_VIDEO, {})
    if not isinstance(video, dict):
        return {}
    block = video.get(YAML_KEY_BUDGET, {})
    return block if isinstance(block, dict) else {}


def load_video_budget_config() -> VideoBudgetConfig:
    """加载预算配置（缺省不限额）。"""
    block = _read_budget_dict()
    limit = float(block.get(YAML_KEY_DEFAULT_LIMIT_USD, DEFAULT_BUDGET_LIMIT_USD))
    fuse_render = bool(block.get(YAML_KEY_FUSE_ON_RENDER, DEFAULT_FUSE_ON_RENDER))
    fuse_compose = bool(block.get(YAML_KEY_FUSE_ON_COMPOSE, DEFAULT_FUSE_ON_COMPOSE))
    return VideoBudgetConfig(
        default_limit_usd=limit,
        fuse_on_render=fuse_render,
        fuse_on_compose=fuse_compose,
    )
