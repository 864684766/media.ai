"""pipeline_job_stale_reconciler 单元测试。"""


def test_stale_when_pipeline_clear_and_shots_validated() -> None:
    """镜头已 validated 且 pipeline 无阻断时，bible 暂停应视为过时。"""
    from app.core.video_pipeline_run_constants import PAUSE_REASON_NO_VALIDATED_SHOTS
    from app.schemas.video_pipeline_state import VideoPipelineState
    from app.video.pipeline_job_stale_reconciler import is_stale_bible_entity_pause

    state = VideoPipelineState(
        project_id="demo",
        paused=True,
        pause_reason=PAUSE_REASON_NO_VALIDATED_SHOTS,
        current_step="validate_entities",
    )
    counts = {"validated": 3, "composed": 2}
    assert is_stale_bible_entity_pause(state, counts, 5) is True


def test_not_stale_when_still_all_rejected() -> None:
    """仍全部 rejected 时不应 reconcile。"""
    from app.core.video_pipeline_run_constants import PAUSE_REASON_NO_VALIDATED_SHOTS
    from app.schemas.video_pipeline_state import VideoPipelineState
    from app.video.pipeline_job_stale_reconciler import is_stale_bible_entity_pause

    state = VideoPipelineState(
        project_id="demo",
        paused=True,
        pause_reason=PAUSE_REASON_NO_VALIDATED_SHOTS,
    )
    counts = {"rejected": 5}
    assert is_stale_bible_entity_pause(state, counts, 5) is False
