"""视频子图 render_shots 节点。"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_run_constants import PAUSE_REASON_NO_VALIDATED_SHOTS
from app.graph.video_nodes.render_shots_failure_helper import (
    patch_render_budget_failure,
    patch_render_generic_failure,
)
from app.graph.video_pipeline_constants import NODE_RENDER_SHOTS
from app.graph.video_pipeline_pause_patch_builder import build_pipeline_pause_patch
from app.graph.video_pipeline_shot_counter import count_validated_shots
from app.schemas.video_pipeline_state import VideoPipelineState
from app.services.render_job_service import start_render_job
from app.video.ffmpeg_required_checker import FfmpegRequiredError
from app.video.project_budget_gate import BudgetExceededError


def run_render_shots_step(session: Session, state: VideoPipelineState) -> dict:
    """对 validated 镜头执行渲染。"""
    if count_validated_shots(session, state.project_id) <= 0:
        return build_pipeline_pause_patch(
            NODE_RENDER_SHOTS,
            PAUSE_REASON_NO_VALIDATED_SHOTS,
            state.steps_completed,
        )
    base = _build_render_base(state)
    return _execute_render(session, state.project_id, base)


def _build_render_base(state: VideoPipelineState) -> dict:
    """构造 render 节点基础 patch。"""
    return {
        "current_step": NODE_RENDER_SHOTS,
        "steps_completed": [*state.steps_completed, NODE_RENDER_SHOTS],
    }


def _execute_render(session: Session, project_id: str, base: dict) -> dict:
    """调用渲染 Job 并处理失败。"""
    try:
        result = start_render_job(session, project_id)
    except BudgetExceededError as exc:
        return patch_render_budget_failure(base, exc)
    except FfmpegRequiredError as exc:
        return patch_render_generic_failure(base, exc)
    base["render_job_id"] = result.job.job_id
    return base
