"""切片渲染分发（V7）。

【职责】
    按 active.clip 选择 stub 文本或 local_ffmpeg mp4。

【何时调用】
    render_job_service 逐镜渲染。
"""

from app.models.postgres.shot_model import ShotModel
from app.video.ffmpeg_required_checker import assert_ffmpeg_for_clip
from app.video.local_ffmpeg_clip_writer import write_local_ffmpeg_clip
from app.video.render_stub_writer import write_clip_stub, write_keyframe_stub
from app.video.shot_render_cost_calculator import calculate_shot_clip_cost
from app.video.video_provider_config_reader import (
    VideoProviderConfig,
    lookup_provider_capability,
)
from app.video.video_provider_constants import (
    VIDEO_PROVIDER_LOCAL_FFMPEG,
    VIDEO_PROVIDER_STUB,
)


def dispatch_clip_render(
    shot: ShotModel,
    config: VideoProviderConfig,
) -> tuple[str, str, str, float]:
    """渲染切片。

    返回:
        tuple: (clip_uri, last_frame_uri, provider_id, cost_usd)。
    """
    provider_id = _resolve_clip_provider(config)
    capability = lookup_provider_capability(config, provider_id)
    cost = calculate_shot_clip_cost(shot, capability)
    assert_ffmpeg_for_clip(config)
    if provider_id == VIDEO_PROVIDER_LOCAL_FFMPEG:
        clip_uri = write_local_ffmpeg_clip(shot)
        frame_uri = write_keyframe_stub(shot)
        return clip_uri, frame_uri, provider_id, cost
    clip_uri, last_frame = write_clip_stub(shot)
    return clip_uri, last_frame, VIDEO_PROVIDER_STUB, cost


def _resolve_clip_provider(config: VideoProviderConfig) -> str:
    """local_ffmpeg 不可用时抛出明确错误。"""
    if config.active_clip != VIDEO_PROVIDER_LOCAL_FFMPEG:
        return config.active_clip
    assert_ffmpeg_for_clip(config)
    return VIDEO_PROVIDER_LOCAL_FFMPEG
