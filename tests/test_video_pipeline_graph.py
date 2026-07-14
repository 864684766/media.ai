"""LangGraph 视频子图运行测试（阶段 D1）。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.core.video_pipeline_run_constants import PAUSE_REASON_NO_SHOTS, PIPELINE_RUN_PAUSED
from app.graph.video_pipeline_constants import NODE_REVIEW_GATE
from app.schemas.video_shot import ShotInput, StoryboardSubmitRequest
from app.services.storyboard_service import submit_storyboard
from app.services.video_pipeline_run_service import run_video_pipeline
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_pipeline_session(monkeypatch):
    """SQLite 内存 Session + API scope mock。"""
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

    monkeypatch.setattr("app.api.video_pipeline.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.video_pipeline.postgres_session_scope", _scope)
    client = TestClient(create_app())
    return factory, client


def test_pipeline_run_pauses_without_shots(pg_pipeline_session) -> None:
    """无分镜时子图应在 validate 暂停。"""
    factory, _client = pg_pipeline_session
    session = factory()
    try:
        result = run_video_pipeline(session, "empty-proj")
    finally:
        session.close()
    assert result.run_status == PIPELINE_RUN_PAUSED
    assert result.pause_reason == PAUSE_REASON_NO_SHOTS
    assert NODE_REVIEW_GATE in result.steps_completed


def test_pipeline_run_via_api_with_storyboard(pg_pipeline_session) -> None:
    """有 draft 分镜时应走完 validate 并进入后续步骤。"""
    factory, client = pg_pipeline_session
    project_id = "pipe-demo"
    session = factory()
    try:
        submit_storyboard(
            session,
            project_id,
            StoryboardSubmitRequest(
                shots=[ShotInput(shot_no="1", duration_sec=2.0, action="测试画面")],
            ),
        )
    finally:
        session.close()
    response = client.post(f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/{project_id}/pipeline/run")
    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == project_id
    assert "validate_entities" in body["steps_completed"]
