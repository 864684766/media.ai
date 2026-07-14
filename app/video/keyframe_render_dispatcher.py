"""关键帧渲染分发（V7）。

【职责】
    按 active.keyframe 写出关键帧（当前均为 SVG Stub）。

【何时调用】
    render_job_service 逐镜渲染。
"""

from app.models.postgres.shot_model import ShotModel
from app.video.render_stub_writer import write_keyframe_stub
from app.video.video_provider_constants import VIDEO_PROVIDER_STUB
from app.video.video_provider_config_reader import VideoProviderConfig


def dispatch_keyframe_render(
    shot: ShotModel,
    config: VideoProviderConfig,
) -> tuple[str, str]:
    """渲染关键帧。

    返回:
        tuple[str, str]: (uri, provider_id)。
    """
    provider_id = config.active_keyframe
    if provider_id == VIDEO_PROVIDER_STUB:
        return write_keyframe_stub(shot), VIDEO_PROVIDER_STUB
    return write_keyframe_stub(shot), provider_id
