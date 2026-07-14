"""视频管线异步 Job 测试（阶段 D3）。"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.video_pipeline_run_constants import PAUSE_REASON_NO_SHOTS
from app.schemas.video_shot import ShotInput, StoryboardSubmitRequest
from app.services.storyboard_service import submit_storyboard
from app.services.video_pipeline_async_service import (
    PipelineJobNotFoundError,
    execute_pipeline_job,
    get_pipeline_job_status,
    resume_pipeline_job,
    start_async_pipeline_job,
)
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pipeline_job_session():
    """SQLite 内存 Session。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_all_tables(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    yield session
    session.close()


def test_async_job_pauses_without_shots(pipeline_job_session) -> None:
    """空项目 Job 应在 validate 后 paused。"""
    job_id = start_async_pipeline_job(pipeline_job_session, "job-empty")
    result = execute_pipeline_job(pipeline_job_session, job_id)
    assert result.pause_reason == PAUSE_REASON_NO_SHOTS
    detail = get_pipeline_job_status(pipeline_job_session, job_id)
    assert detail.paused is True


def test_resume_job_not_found(pipeline_job_session) -> None:
    """不存在 Job 应抛 PipelineJobNotFoundError。"""
    with pytest.raises(PipelineJobNotFoundError):
        resume_pipeline_job(pipeline_job_session, "missing-id")


def test_async_job_with_storyboard_runs_validate(pipeline_job_session) -> None:
    """有分镜时 Job 应完成 validate 步骤。"""
    project_id = "async-demo"
    submit_storyboard(
        pipeline_job_session,
        project_id,
        StoryboardSubmitRequest(
            shots=[ShotInput(shot_no="1", duration_sec=2.0, action="画面")],
        ),
    )
    job_id = start_async_pipeline_job(pipeline_job_session, project_id)
    result = execute_pipeline_job(pipeline_job_session, job_id)
    assert "validate_entities" in result.steps_completed
