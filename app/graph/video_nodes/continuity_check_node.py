"""视频子图 continuity_check 节点。"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_run_constants import PAUSE_REASON_NO_VALIDATED_SHOTS
from app.graph.video_pipeline_constants import NODE_CONTINUITY_CHECK
from app.graph.video_pipeline_pause_patch_builder import build_pipeline_pause_patch
from app.graph.video_pipeline_shot_counter import count_rendered_shots
from app.schemas.video_pipeline_state import VideoPipelineState
from app.services.continuity_qa_service import run_continuity_qa


def run_continuity_check_step(session: Session, state: VideoPipelineState) -> dict:
    """对 rendered 镜头执行连续性 QA。"""
    if count_rendered_shots(session, state.project_id) <= 0:
        return build_pipeline_pause_patch(
            NODE_CONTINUITY_CHECK,
            PAUSE_REASON_NO_VALIDATED_SHOTS,
            state.steps_completed,
        )
    result = run_continuity_qa(session, state.project_id)
    base = {
        "current_step": NODE_CONTINUITY_CHECK,
        "steps_completed": [*state.steps_completed, NODE_CONTINUITY_CHECK],
        "qa_passed_count": result.passed_count,
        "qa_awaiting_count": result.awaiting_review_count,
    }
    if result.awaiting_review_count > 0:
        from app.core.video_pipeline_run_constants import (
            PAUSE_REASON_AWAITING_REVIEW,
            PIPELINE_RUN_PAUSED,
        )

        base["paused"] = True
        base["run_status"] = PIPELINE_RUN_PAUSED
        base["pause_reason"] = PAUSE_REASON_AWAITING_REVIEW
    return base
