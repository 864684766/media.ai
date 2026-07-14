"""视频子图条件边路由。"""

from app.core.video_pipeline_run_constants import (
    BRANCH_PIPELINE_CONTINUE,
    BRANCH_PIPELINE_PAUSE,
    PIPELINE_RUN_FAILED,
)
from app.schemas.video_pipeline_state import VideoPipelineState


def route_after_review_gate(state: VideoPipelineState) -> str:
    """review_gate 之后：暂停则结束子图。

    参数:
        state: 当前子图状态。

    返回:
        str: continue 或 pause 分支名。
    """
    if state.paused or state.run_status == PIPELINE_RUN_FAILED:
        return BRANCH_PIPELINE_PAUSE
    return BRANCH_PIPELINE_CONTINUE


def route_after_continuity_check(state: VideoPipelineState) -> str:
    """QA 之后：有 awaiting_review 或已失败则暂停。

    参数:
        state: 当前子图状态。

    返回:
        str: continue 或 pause 分支名。
    """
    if state.paused or state.run_status == PIPELINE_RUN_FAILED:
        return BRANCH_PIPELINE_PAUSE
    return BRANCH_PIPELINE_CONTINUE


def route_after_audio_pipeline(state: VideoPipelineState) -> str:
    """audio 之后：等待 BGM 或已失败则暂停，否则进入 compose。

    参数:
        state: 当前子图状态。

    返回:
        str: continue 或 pause 分支名。
    """
    if state.paused or state.run_status == PIPELINE_RUN_FAILED:
        return BRANCH_PIPELINE_PAUSE
    return BRANCH_PIPELINE_CONTINUE
