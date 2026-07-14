"""ffmpeg 可用性校验（真实音视频模式）。"""

from app.video.ffmpeg_binary_resolver import is_ffmpeg_available
from app.video.video_provider_config_reader import VideoProviderConfig
from app.video.video_provider_constants import (
    COMPOSE_PROVIDER_LOCAL_FFMPEG,
    VIDEO_PROVIDER_LOCAL_FFMPEG,
)


class FfmpegRequiredError(RuntimeError):
    """配置要求 ffmpeg 但系统未安装。"""


def assert_ffmpeg_for_clip(config: VideoProviderConfig) -> None:
    """clip=local_ffmpeg 时要求 ffmpeg 可用。"""
    if config.active_clip != VIDEO_PROVIDER_LOCAL_FFMPEG:
        return
    if not is_ffmpeg_available():
        raise FfmpegRequiredError("未找到 ffmpeg：请安装并加入 PATH，或设置 FFMPEG_PATH")


def assert_ffmpeg_for_compose(config: VideoProviderConfig, clip_uris: list[str]) -> None:
    """compose=local_ffmpeg 时要求 ffmpeg 与 mp4 clip。"""
    if config.active_compose != COMPOSE_PROVIDER_LOCAL_FFMPEG:
        return
    if not is_ffmpeg_available():
        raise FfmpegRequiredError("未找到 ffmpeg：请安装并加入 PATH，或设置 FFMPEG_PATH")
    if not clip_uris or not all(uri.endswith(".mp4") for uri in clip_uris):
        raise FfmpegRequiredError("合成 mp4 需要全部镜头 clip 为 .mp4，请先 local_ffmpeg 渲染")
