"""视频子图 validate_entities 节点。"""

from sqlalchemy.orm import Session

from app.core.video_pipeline_run_constants import (
    PAUSE_REASON_ALL_SHOTS_REJECTED,
    PAUSE_REASON_NO_SHOTS,
    PAUSE_REASON_NO_VALIDATED_SHOTS,
)
from app.graph.video_pipeline_constants import NODE_VALIDATE_ENTITIES
from app.graph.video_pipeline_pause_patch_builder import build_pipeline_pause_patch
from app.graph.video_pipeline_shot_counter import (
    count_project_shots,
    count_rejected_shots,
    count_validated_shots,
)
from app.graph.video_nodes.validate_entities_pending_checker import (
    has_entity_validation_pending,
)
from app.schemas.video_pipeline_state import VideoPipelineState
from app.services.entity_validation_service import validate_project_entities


def run_validate_entities_step(session: Session, state: VideoPipelineState) -> dict:
    """校验 draft/rejected 镜头实体引用。"""
    if count_project_shots(session, state.project_id) == 0:
        return _pause(state, PAUSE_REASON_NO_SHOTS)
    if not has_entity_validation_pending(session, state.project_id):
        return _resolve_non_draft(session, state)
    result = validate_project_entities(session, state.project_id)
    if result.validated_count <= 0:
        return _pause(state, PAUSE_REASON_ALL_SHOTS_REJECTED)
    return _build_validate_update(state, result.validated_count)


def _resolve_non_draft(session: Session, state: VideoPipelineState) -> dict:
    """无 draft 时：有 validated 则跳过，否则暂停。"""
    if count_validated_shots(session, state.project_id) > 0:
        return _skip_validate(state)
    if count_rejected_shots(session, state.project_id) > 0:
        return _pause(state, PAUSE_REASON_ALL_SHOTS_REJECTED)
    return _pause(state, PAUSE_REASON_NO_VALIDATED_SHOTS)


def _pause(state: VideoPipelineState, reason: str) -> dict:
    """校验阶段暂停。"""
    return build_pipeline_pause_patch(NODE_VALIDATE_ENTITIES, reason, state.steps_completed)


def _skip_validate(state: VideoPipelineState) -> dict:
    """无 draft 且已有 validated 时跳过。"""
    return {
        "current_step": NODE_VALIDATE_ENTITIES,
        "steps_completed": [*state.steps_completed, NODE_VALIDATE_ENTITIES],
    }


def _build_validate_update(state: VideoPipelineState, validated: int) -> dict:
    """构造校验完成更新。"""
    return {
        "validate_validated_count": validated,
        "current_step": NODE_VALIDATE_ENTITIES,
        "steps_completed": [*state.steps_completed, NODE_VALIDATE_ENTITIES],
    }
