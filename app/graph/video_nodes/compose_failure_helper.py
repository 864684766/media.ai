"""compose 节点失败处理。"""

from app.graph.video_pipeline_failure_patch_builder import build_pipeline_failure_patch
from app.services.compose_job_service import ComposeBlockedError
from app.video.ffmpeg_required_checker import FfmpegRequiredError


def patch_compose_blocked(base: dict, exc: ComposeBlockedError) -> dict:
    """合成阻断失败 patch。"""
    message = exc.reasons[0] if exc.reasons else "compose blocked"
    return build_pipeline_failure_patch(base, message)


def patch_compose_ffmpeg_failure(base: dict, exc: FfmpegRequiredError) -> dict:
    """ffmpeg 不可用失败 patch。"""
    return build_pipeline_failure_patch(base, str(exc))
