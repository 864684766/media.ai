"""连续性 QA API 测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core.video_constants import VIDEO_ROUTE_PREFIX
from app.models.postgres.shot_model import ShotModel  # noqa: F401
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_qa_client(monkeypatch, tmp_path) -> TestClient:
    """SQLite 内存库 TestClient（含 render + qa）。"""
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

    for module in (
        "app.api.video",
        "app.api.video_bible",
        "app.api.video_render",
        "app.api.video_qa",
    ):
        monkeypatch.setattr(f"{module}.is_postgres_configured", lambda: True)
        monkeypatch.setattr(f"{module}.postgres_session_scope", _scope)

    monkeypatch.setattr(
        "app.video.video_assets_config_reader.load_video_assets_config",
        lambda: type("Cfg", (), {"assets_dir": str(assets_dir)})(),
    )
    return TestClient(create_app())


def _render_demo_shots(client: TestClient, shots: list[dict]) -> None:
    """提交分镜、校验并渲染。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo"
    client.post(f"{base}/storyboard", json={"shots": shots})
    client.put(
        f"{base}/bible/scenes",
        json={"scenes": [{"scene_id": "s1", "name": "A"}, {"scene_id": "s2", "name": "B"}]},
    )
    client.put(
        f"{base}/bible/props",
        json={"props": [{"prop_id": "p1", "name": "剑"}]},
    )
    client.post(f"{base}/validate")
    client.post(f"{base}/render")


def test_qa_passes_rendered_shot(pg_qa_client: TestClient) -> None:
    """单镜 rendered 且有关键帧时应 qa_passed。"""
    _render_demo_shots(
        pg_qa_client,
        [{"shot_no": "1", "duration_sec": 3, "scene_id": "s1", "action": "推门"}],
    )
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/qa"
    response = pg_qa_client.post(url)
    assert response.status_code == 200
    payload = response.json()
    assert payload["passed_count"] == 1
    assert payload["failed_count"] == 0


def test_qa_fails_missing_transition(pg_qa_client: TestClient) -> None:
    """场景跳变无 transition 应 qa_failed。"""
    _render_demo_shots(
        pg_qa_client,
        [
            {"shot_no": "1", "duration_sec": 3, "scene_id": "s1"},
            {"shot_no": "2", "duration_sec": 3, "scene_id": "s2"},
        ],
    )
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/qa"
    payload = pg_qa_client.post(url).json()
    assert payload["failed_count"] == 1
    assert "missing_transition" in payload["failures"][0]["reasons"][0]


def test_qa_fails_prop_dropped(pg_qa_client: TestClient) -> None:
    """同场景道具丢失应 qa_failed。"""
    _render_demo_shots(
        pg_qa_client,
        [
            {"shot_no": "1", "duration_sec": 3, "scene_id": "s1", "prop_ids": ["p1"]},
            {"shot_no": "2", "duration_sec": 3, "scene_id": "s1", "prop_ids": []},
        ],
    )
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/qa"
    payload = pg_qa_client.post(url).json()
    assert payload["failed_count"] == 1
    assert "prop_dropped" in payload["failures"][0]["reasons"][0]
