"""pytest 全局 fixtures。"""

import pytest

from app.video.provider_capability_model import ProviderCapability
from app.video.video_provider_config_reader import VideoProviderConfig
from app.video.video_provider_constants import (
    COMPOSE_PROVIDER_STUB_JSON,
    VIDEO_PROVIDER_STUB,
)

# 测试环境强制 Stub Provider，避免依赖本机 ffmpeg 与 app.yaml 真实 AV 默认
_STUB_CAPABILITY = ProviderCapability(
    provider_id=VIDEO_PROVIDER_STUB,
    max_ref_images=1,
    max_ref_videos=0,
    native_audio=False,
    multi_shot=False,
    cost_per_second=0.0,
)

_STUB_JSON_CAPABILITY = ProviderCapability(
    provider_id=COMPOSE_PROVIDER_STUB_JSON,
    max_ref_images=0,
    max_ref_videos=0,
    native_audio=False,
    multi_shot=False,
    cost_per_second=0.0,
)

STUB_VIDEO_PROVIDER_CONFIG = VideoProviderConfig(
    active_keyframe=VIDEO_PROVIDER_STUB,
    active_clip=VIDEO_PROVIDER_STUB,
    active_compose=COMPOSE_PROVIDER_STUB_JSON,
    matrix={
        VIDEO_PROVIDER_STUB: _STUB_CAPABILITY,
        COMPOSE_PROVIDER_STUB_JSON: _STUB_JSON_CAPABILITY,
    },
)

_PROVIDER_PATCH_TARGETS = (
    "app.video.video_provider_config_reader.load_video_provider_config",
    "app.services.render_job_service.load_video_provider_config",
    "app.services.compose_job_service.load_video_provider_config",
    "app.services.video_cost_service.load_video_provider_config",
    "app.services.mcp_single_shot_render_service.load_video_provider_config",
)


def _return_stub_config() -> VideoProviderConfig:
    """供 monkeypatch 使用的 Stub 配置工厂。"""
    return STUB_VIDEO_PROVIDER_CONFIG


@pytest.fixture(autouse=True)
def stub_video_providers_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """全量测试默认 Stub 视频 Provider，与 app.yaml 真实 AV 默认解耦。"""
    for target in _PROVIDER_PATCH_TARGETS:
        monkeypatch.setattr(target, _return_stub_config)
