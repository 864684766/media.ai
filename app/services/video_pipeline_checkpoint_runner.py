"""视频子图分步执行（checkpoint 友好）。"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_run_constants import PIPELINE_RUN_FAILED
from app.graph.video_nodes.audio_pipeline_node import run_audio_pipeline_step
from app.graph.video_nodes.compose_node import run_compose_step
from app.graph.video_nodes.continuity_check_node import run_continuity_check_step
from app.graph.video_nodes.render_shots_node import run_render_shots_step
from app.graph.video_nodes.review_gate_node import run_review_gate_step
from app.graph.video_nodes.validate_entities_node import run_validate_entities_step
from app.graph.video_pipeline_constants import (
    NODE_AUDIO_PIPELINE,
    NODE_COMPOSE,
    NODE_CONTINUITY_CHECK,
    NODE_RENDER_SHOTS,
    NODE_REVIEW_GATE,
    NODE_VALIDATE_ENTITIES,
)
from app.schemas.video_pipeline_state import VideoPipelineState

PIPELINE_STEP_ORDER: tuple[str, ...] = (
    NODE_VALIDATE_ENTITIES,
    NODE_REVIEW_GATE,
    NODE_RENDER_SHOTS,
    NODE_CONTINUITY_CHECK,
    NODE_AUDIO_PIPELINE,
    NODE_COMPOSE,
)

_STEP_RUNNERS = {
    NODE_VALIDATE_ENTITIES: run_validate_entities_step,
    NODE_REVIEW_GATE: run_review_gate_step,
    NODE_RENDER_SHOTS: run_render_shots_step,
    NODE_CONTINUITY_CHECK: run_continuity_check_step,
    NODE_AUDIO_PIPELINE: run_audio_pipeline_step,
    NODE_COMPOSE: run_compose_step,
}


def run_pipeline_from_step_index(
    session: Session,
    state: VideoPipelineState,
    start_index: int = 0,
) -> VideoPipelineState:
    """从指定步骤起顺序执行并合并 state。

    参数:
        session: PG Session。
        state: 初始 state。
        start_index: PIPELINE_STEP_ORDER 起始下标。

    返回:
        VideoPipelineState: 执行后终态。
    """
    current = state
    for step_id in PIPELINE_STEP_ORDER[start_index:]:
        patch = _STEP_RUNNERS[step_id](session, current)
        current = current.model_copy(update=patch)
        if _should_stop(current):
            break
    return current


def resolve_resume_step_index(state: VideoPipelineState) -> int:
    """根据 steps_completed 计算续跑起点。"""
    completed = set(state.steps_completed)
    for index, step_id in enumerate(PIPELINE_STEP_ORDER):
        if step_id not in completed:
            return index
    return len(PIPELINE_STEP_ORDER)


def _should_stop(state: VideoPipelineState) -> bool:
    """暂停或失败时停止后续步骤。"""
    return state.paused or state.run_status == PIPELINE_RUN_FAILED
