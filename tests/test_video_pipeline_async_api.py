"""视频管线异步 Job HTTP API 测试（阶段 E2）。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.core.video_pipeline_job_constants import (
    PIPELINE_JOB_ROUTE_PREFIX,
    PIPELINE_JOB_STATUS_PENDING,
    PIPELINE_JOB_STATUS_PAUSED,
)
from app.core.video_pipeline_run_constants import PAUSE_REASON_NO_SHOTS
from app.schemas.video_shot import ShotInput, StoryboardSubmitRequest
from app.services.storyboard_service import submit_storyboard
from app.services.video_pipeline_async_service import execute_pipeline_job
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_async_pipeline_client(monkeypatch):
    """SQLite 内存库 + 同步执行 worker 的 TestClient。"""
    from app.application import create_app

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_all_tables(engine)
    factory = sessionmaker(bind=engine)

    class _SessionScope:
        """模拟 postgres_session_scope。"""

        def __enter__(self):
            self._session = factory()
            return self._session

        def __exit__(self, *args):
            self._session.close()

    def _scope():
        return _SessionScope()

    def _sync_worker(job_id: str) -> None:
        """测试用：后台线程改为同步执行。"""
        with _scope() as session:
            execute_pipeline_job(session, job_id)

    monkeypatch.setattr("app.api.video_pipeline.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.video_pipeline.postgres_session_scope", _scope)
    monkeypatch.setattr("app.api.video_pipeline.spawn_pipeline_worker", _sync_worker)
    client = TestClient(create_app())
    return factory, client


def test_post_run_async_returns_job_id(pg_async_pipeline_client) -> None:
    """POST run/async 应返回 pending 与 job_id。"""
    _factory, client = pg_async_pipeline_client
    project_id = "async-api-empty"
    response = client.post(
        f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/{project_id}/pipeline/run/async",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == project_id
    assert body["status"] == PIPELINE_JOB_STATUS_PENDING
    assert body["job_id"]


def test_get_pipeline_job_returns_checkpoint(pg_async_pipeline_client) -> None:
    """GET jobs/{id} 应返回 paused checkpoint。"""
    _factory, client = pg_async_pipeline_client
    project_id = "async-api-check"
    start = client.post(
        f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/{project_id}/pipeline/run/async",
    )
    job_id = start.json()["job_id"]
    detail = client.get(f"/api/v1{VIDEO_ROUTE_PREFIX}{PIPELINE_JOB_ROUTE_PREFIX}/{job_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["job_id"] == job_id
    assert body["status"] == PIPELINE_JOB_STATUS_PAUSED
    assert body["run"]["pause_reason"] == PAUSE_REASON_NO_SHOTS


def test_resume_pipeline_job_continues(pg_async_pipeline_client) -> None:
    """POST resume 应从 checkpoint 继续执行。"""
    factory, client = pg_async_pipeline_client
    project_id = "async-api-resume"
    start = client.post(
        f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/{project_id}/pipeline/run/async",
    )
    job_id = start.json()["job_id"]
    session = factory()
    try:
        submit_storyboard(
            session,
            project_id,
            StoryboardSubmitRequest(
                shots=[ShotInput(shot_no="1", duration_sec=2.0, action="续跑测试")],
            ),
        )
    finally:
        session.close()
    resumed = client.post(
        f"/api/v1{VIDEO_ROUTE_PREFIX}{PIPELINE_JOB_ROUTE_PREFIX}/{job_id}/resume",
    )
    assert resumed.status_code == 200
    body = resumed.json()
    assert "validate_entities" in body["run"]["steps_completed"]


def test_get_pipeline_job_not_found(pg_async_pipeline_client) -> None:
    """不存在 Job 应 404。"""
    _factory, client = pg_async_pipeline_client
    response = client.get(
        f"/api/v1{VIDEO_ROUTE_PREFIX}{PIPELINE_JOB_ROUTE_PREFIX}/missing-job",
    )
    assert response.status_code == 404
