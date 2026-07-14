"""视频 Provider 配置读取（V7）。

【职责】
    从 app.yaml video.providers 读取 active 选型与能力矩阵。

【何时调用】
    渲染/合成 Job 启动前由分发器读取。

【简例】
    cfg = load_video_provider_config()
    clip_id = cfg.active_clip  # → "stub"
"""

from dataclasses import dataclass

from app.core.config_yaml_loader import load_app_yaml
from app.video.provider_capability_model import ProviderCapability
from app.video.video_config_constants import YAML_KEY_VIDEO
from app.video.video_provider_constants import (
    CAP_KEY_COST_PER_SECOND,
    CAP_KEY_MAX_REF_IMAGES,
    CAP_KEY_MAX_REF_VIDEOS,
    CAP_KEY_MULTI_SHOT,
    CAP_KEY_NATIVE_AUDIO,
    COMPOSE_PROVIDER_STUB_JSON,
    DEFAULT_ACTIVE_CLIP_PROVIDER,
    DEFAULT_ACTIVE_COMPOSE_PROVIDER,
    DEFAULT_ACTIVE_KEYFRAME_PROVIDER,
    YAML_KEY_ACTIVE,
    YAML_KEY_ACTIVE_CLIP,
    YAML_KEY_ACTIVE_COMPOSE,
    YAML_KEY_ACTIVE_KEYFRAME,
    YAML_KEY_MATRIX,
    YAML_KEY_PROVIDERS,
)


@dataclass(frozen=True)
class VideoProviderConfig:
    """Provider 选型与矩阵。"""

    active_keyframe: str
    active_clip: str
    active_compose: str
    matrix: dict[str, ProviderCapability]


def _read_providers_block() -> dict:
    """取出 video.providers 字典。"""
    root = load_app_yaml()
    video = root.get(YAML_KEY_VIDEO, {})
    if not isinstance(video, dict):
        return {}
    block = video.get(YAML_KEY_PROVIDERS, {})
    return block if isinstance(block, dict) else {}


def _read_active_ids(block: dict) -> tuple[str, str, str]:
    """解析 active 三段 Provider id。"""
    active = block.get(YAML_KEY_ACTIVE, {})
    if not isinstance(active, dict):
        active = {}
    keyframe = str(active.get(YAML_KEY_ACTIVE_KEYFRAME, DEFAULT_ACTIVE_KEYFRAME_PROVIDER))
    clip = str(active.get(YAML_KEY_ACTIVE_CLIP, DEFAULT_ACTIVE_CLIP_PROVIDER))
    compose = str(active.get(YAML_KEY_ACTIVE_COMPOSE, DEFAULT_ACTIVE_COMPOSE_PROVIDER))
    return keyframe, clip, compose


def _parse_capability(provider_id: str, raw: dict) -> ProviderCapability:
    """将 YAML 字典转为 ProviderCapability。"""
    if not isinstance(raw, dict):
        raw = {}
    return ProviderCapability(
        provider_id=provider_id,
        max_ref_images=int(raw.get(CAP_KEY_MAX_REF_IMAGES, 1)),
        max_ref_videos=int(raw.get(CAP_KEY_MAX_REF_VIDEOS, 0)),
        native_audio=bool(raw.get(CAP_KEY_NATIVE_AUDIO, False)),
        multi_shot=bool(raw.get(CAP_KEY_MULTI_SHOT, False)),
        cost_per_second=float(raw.get(CAP_KEY_COST_PER_SECOND, 0.0)),
    )


def _read_matrix(block: dict) -> dict[str, ProviderCapability]:
    """解析 matrix 下全部 Provider 能力。"""
    matrix_raw = block.get(YAML_KEY_MATRIX, {})
    if not isinstance(matrix_raw, dict):
        return {}
    return {
        str(pid): _parse_capability(str(pid), caps)
        for pid, caps in matrix_raw.items()
    }


def load_video_provider_config() -> VideoProviderConfig:
    """加载 Provider 配置（缺省走常量默认）。"""
    block = _read_providers_block()
    keyframe, clip, compose = _read_active_ids(block)
    matrix = _read_matrix(block)
    if COMPOSE_PROVIDER_STUB_JSON not in matrix:
        matrix[COMPOSE_PROVIDER_STUB_JSON] = _parse_capability(COMPOSE_PROVIDER_STUB_JSON, {})
    return VideoProviderConfig(
        active_keyframe=keyframe,
        active_clip=clip,
        active_compose=compose,
        matrix=matrix,
    )


def lookup_provider_capability(
    config: VideoProviderConfig,
    provider_id: str,
) -> ProviderCapability:
    """按 id 查能力；未知 Provider 返回零成本默认能力。"""
    found = config.matrix.get(provider_id)
    if found is not None:
        return found
    return ProviderCapability(provider_id=provider_id)
