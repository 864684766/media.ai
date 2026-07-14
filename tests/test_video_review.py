"""V6 HITL review 与 pipeline API 测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core.video_constants import (
    REVIEW_ACTION_APPROVE,
    REVIEW_STAGE_QA_OVERFLOW,
    VIDEO_ROUTE_PREFIX,
)
from app.models.postgres.shot_model import ShotModel  # noqa: F401
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_v6_client(monkeypatch, tmp_path) -> TestClient:
    """SQLite 内存库 TestClient（含 V6 API）。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_all_tables(engine)
    factory = sessionmaker(bind=engine)
    assets_dir = tmp_path / "video_assets"
    assets_dir.mkdir()

    class _SessionScope:
        """模拟 postgres_session_scope。"""

        def __enter__(self):
            self._session = factory()
            return self._session

        def __exit__(self, *args):
            self._session.close()

    def _scope():
        return _SessionScope()

    modules = (
        "app.api.video",
        "app.api.video_bible",
        "app.api.video_render",
        "app.api.video_qa",
        "app.api.video_review",
        "app.api.video_pipeline",
    )
    for module in modules:
        monkeypatch.setattr(f"{module}.is_postgres_configured", lambda: True)
        monkeypatch.setattr(f"{module}.postgres_session_scope", _scope)

    monkeypatch.setattr(
        "app.video.video_assets_config_reader.load_video_assets_config",
        lambda: type("Cfg", (), {"assets_dir": str(assets_dir)})(),
    )
    monkeypatch.setattr(
        "app.services.continuity_qa_service.load_video_qa_config",
        lambda: type("Cfg", (), {"max_retries": 1})(),
    )
    return TestClient(create_app())


def _awaiting_review_shot(client: TestClient) -> str:
    """制造 awaiting_review 镜头并返回 shot_id。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo"
    client.post(
        f"{base}/storyboard",
        json={
            "shots": [
                {"shot_no": "1", "duration_sec": 3, "scene_id": "s1"},
                {"shot_no": "2", "duration_sec": 3, "scene_id": "s2"},
            ]
        },
    )
    client.put(
        f"{base}/bible/scenes",
        json={
            "scenes": [
                {"scene_id": "s1", "name": "A"},
                {"scene_id": "s2", "name": "B"},
            ]
        },
    )
    client.post(f"{base}/validate")
    client.post(f"{base}/render")
    client.post(f"{base}/qa")
    pipeline = client.get(f"{base}/pipeline").json()
    assert len(pipeline["awaiting_review"]) == 1
    return pipeline["awaiting_review"][0]["shot_id"]


def test_pipeline_status_counts(pg_v6_client: TestClient) -> None:
    """GET pipeline 应返回状态计数与步骤。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo"
    pg_v6_client.post(
        f"{base}/storyboard",
        json={"shots": [{"shot_no": "1", "duration_sec": 3, "scene_id": "s1"}]},
    )
    response = pg_v6_client.get(f"{base}/pipeline")
    assert response.status_code == 200
    payload = response.json()
    assert payload["shots_total"] == 1
    assert payload["status_counts"]["draft"] == 1
    assert len(payload["steps"]) == 5


def test_review_approve_awaiting_review(pg_v6_client: TestClient) -> None:
    """人工通过 awaiting_review 应变为 qa_passed。"""
    shot_id = _awaiting_review_shot(pg_v6_client)
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/shots/{shot_id}/review"
    body = {"stage": REVIEW_STAGE_QA_OVERFLOW, "action": REVIEW_ACTION_APPROVE}
    response = pg_v6_client.post(url, json=body)
    assert response.status_code == 200
    assert response.json()["shot"]["status"] == "qa_passed"


def test_review_rejects_invalid_transition(pg_v6_client: TestClient) -> None:
    """非法阶段/状态组合应 400。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo"
    pg_v6_client.post(
        f"{base}/storyboard",
        json={"shots": [{"shot_no": "1", "duration_sec": 3}]},
    )
    shots = pg_v6_client.get(f"{base}/shots").json()["shots"]
    shot_id = shots[0]["shot_id"]
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/shots/{shot_id}/review"
    body = {"stage": REVIEW_STAGE_QA_OVERFLOW, "action": REVIEW_ACTION_APPROVE}
    response = pg_v6_client.post(url, json=body)
    assert response.status_code == 400
