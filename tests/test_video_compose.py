"""视频合成 API 测试（V5）。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core.video_constants import VIDEO_ROUTE_PREFIX
from app.models.postgres.compose_job_model import ComposeJobModel  # noqa: F401
from app.models.postgres.shot_model import ShotModel  # noqa: F401
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_compose_client(monkeypatch, tmp_path) -> TestClient:
    """SQLite 内存库 TestClient（render + qa + compose）。"""
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
        "app.api.video_compose",
    ):
        monkeypatch.setattr(f"{module}.is_postgres_configured", lambda: True)
        monkeypatch.setattr(f"{module}.postgres_session_scope", _scope)

    monkeypatch.setattr(
        "app.video.video_assets_config_reader.load_video_assets_config",
        lambda: type("Cfg", (), {"assets_dir": str(assets_dir)})(),
    )
    return TestClient(create_app())


def _qa_ready_pipeline(client: TestClient) -> None:
    """走完 storyboard → validate → render → qa。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo"
    client.post(
        f"{base}/storyboard",
        json={"shots": [{"shot_no": "1", "duration_sec": 3, "scene_id": "s1"}]},
    )
    client.put(
        f"{base}/bible/scenes",
        json={"scenes": [{"scene_id": "s1", "name": "A"}]},
    )
    client.post(f"{base}/validate")
    client.post(f"{base}/render")
    client.post(f"{base}/qa")


def test_compose_writes_timeline_stub(pg_compose_client: TestClient) -> None:
    """POST compose 应产出 timeline Stub 与 Job。"""
    _qa_ready_pipeline(pg_compose_client)
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/compose"
    response = pg_compose_client.post(url)
    assert response.status_code == 200
    payload = response.json()
    assert payload["job"]["status"] == "completed"
    assert payload["job"]["total_shots"] == 1
    assert "timeline.stub.json" in payload["output"]["uri"]


def test_compose_file_api_serves_json(pg_compose_client: TestClient) -> None:
    """files API 应能打开合成 JSON。"""
    _qa_ready_pipeline(pg_compose_client)
    compose_url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/compose"
    output = pg_compose_client.post(compose_url).json()["output"]
    response = pg_compose_client.get(output["open_url"])
    assert response.status_code == 200
    assert "clips" in response.text


def test_compose_rejects_without_qa_passed(pg_compose_client: TestClient) -> None:
    """无 qa_passed 镜头时应 400。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo"
    pg_compose_client.post(
        f"{base}/storyboard",
        json={"shots": [{"shot_no": "1", "duration_sec": 3}]},
    )
    response = pg_compose_client.post(f"{base}/compose")
    assert response.status_code == 400


def test_get_compose_job(pg_compose_client: TestClient) -> None:
    """GET compose/jobs 应返回 Job。"""
    _qa_ready_pipeline(pg_compose_client)
    compose_url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/compose"
    job_id = pg_compose_client.post(compose_url).json()["job"]["job_id"]
    get_url = f"/api/v1{VIDEO_ROUTE_PREFIX}/compose/jobs/{job_id}"
    response = pg_compose_client.get(get_url)
    assert response.status_code == 200
    assert response.json()["output_uri"]
