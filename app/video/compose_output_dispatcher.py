"""合成产物分发（V7）。

【职责】
    按 active.compose 写出 JSON Stub 或 ffmpeg timeline.mp4。

【何时调用】
    compose_job_service 落盘阶段。
"""

from app.video.compose_stub_writer import write_compose_stub
from app.video.ffmpeg_required_checker import assert_ffmpeg_for_compose
from app.video.local_ffmpeg_compose_writer import write_local_ffmpeg_compose
from app.video.video_provider_config_reader import VideoProviderConfig
from app.video.video_provider_constants import (
    COMPOSE_PROVIDER_LOCAL_FFMPEG,
    COMPOSE_PROVIDER_STUB_JSON,
)


def dispatch_compose_output(
    project_id: str,
    timeline_payload: dict,
    clip_uris: list[str],
    config: VideoProviderConfig,
) -> str:
    """写出合成产物并返回相对 URI。"""
    mode = _resolve_compose_mode(config, clip_uris)
    if mode == COMPOSE_PROVIDER_LOCAL_FFMPEG:
        return write_local_ffmpeg_compose(project_id, clip_uris, timeline_payload)
    return write_compose_stub(project_id, timeline_payload)


def _resolve_compose_mode(config: VideoProviderConfig, clip_uris: list[str]) -> str:
    """local_ffmpeg 需全部 clip 为 mp4 且二进制可用。"""
    if config.active_compose != COMPOSE_PROVIDER_LOCAL_FFMPEG:
        return COMPOSE_PROVIDER_STUB_JSON
    assert_ffmpeg_for_compose(config, clip_uris)
    return COMPOSE_PROVIDER_LOCAL_FFMPEG
