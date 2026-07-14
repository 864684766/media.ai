"""Provider 能力矩阵条目。"""

from dataclasses import dataclass

from app.video.video_provider_constants import (
    DEFAULT_MAX_REF_IMAGES,
    DEFAULT_MAX_REF_VIDEOS,
    DEFAULT_MULTI_SHOT,
    DEFAULT_NATIVE_AUDIO,
    DEFAULT_PROVIDER_COST_PER_SECOND,
)


@dataclass(frozen=True)
class ProviderCapability:
    """单 Provider 能力位与计费单价。

    字段:
        provider_id: Provider 标识。
        max_ref_images: 最大参考图数量。
        max_ref_videos: 最大参考视频数量。
        native_audio: 是否原生带音频。
        multi_shot: 是否支持多镜连贯模式。
        cost_per_second: 按秒计费单价（美元占位）。
    """

    provider_id: str
    max_ref_images: int = DEFAULT_MAX_REF_IMAGES
    max_ref_videos: int = DEFAULT_MAX_REF_VIDEOS
    native_audio: bool = DEFAULT_NATIVE_AUDIO
    multi_shot: bool = DEFAULT_MULTI_SHOT
    cost_per_second: float = DEFAULT_PROVIDER_COST_PER_SECOND
