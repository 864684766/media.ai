"""视频子图 compose 节点。"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_run_constants import (
    PAUSE_REASON_COMPOSE_BLOCKED,
    PIPELINE_RUN_COMPLETED,
)
from app.graph.video_nodes.compose_failure_helper import (
    patch_compose_blocked,
    patch_compose_ffmpeg_failure,
)
from app.graph.video_pipeline_constants import NODE_COMPOSE
from app.graph.video_pipeline_pause_patch_builder import build_pipeline_pause_patch
from app.graph.video_pipeline_shot_counter import count_project_shots
from app.schemas.video_pipeline_state import VideoPipelineState
from app.services.compose_job_service import ComposeBlockedError, start_compose_job
from app.storage.postgres.shot_repository import ShotRepository
from app.video.ffmpeg_required_checker import FfmpegRequiredError


def run_compose_step(session: Session, state: VideoPipelineState) -> dict:
    """将 qa_passed 镜头合成时间轴成片。"""
    passed = ShotRepository(session).list_qa_passed_by_project(state.project_id)
    if not passed:
        return _pause_when_no_passed(session, state)
    base = _build_compose_base(state)
    return _execute_compose(session, state.project_id, base)


def _pause_when_no_passed(session: Session, state: VideoPipelineState) -> dict:
    """无 qa_passed 镜头时暂停或跳过。"""
    if count_project_shots(session, state.project_id) == 0:
        return {"current_step": NODE_COMPOSE}
    return build_pipeline_pause_patch(
        NODE_COMPOSE,
        PAUSE_REASON_COMPOSE_BLOCKED,
        state.steps_completed,
    )


def _build_compose_base(state: VideoPipelineState) -> dict:
    """构造 compose 节点基础 patch。"""
    return {
        "current_step": NODE_COMPOSE,
        "steps_completed": [*state.steps_completed, NODE_COMPOSE],
    }


def _execute_compose(session: Session, project_id: str, base: dict) -> dict:
    """调用合成 Job 并处理失败。"""
    try:
        result = start_compose_job(session, project_id)
    except ComposeBlockedError as exc:
        return patch_compose_blocked(base, exc)
    except FfmpegRequiredError as exc:
        return patch_compose_ffmpeg_failure(base, exc)
    base["compose_output_uri"] = result.output.uri
    base["run_status"] = PIPELINE_RUN_COMPLETED
    base["paused"] = False
    return base
