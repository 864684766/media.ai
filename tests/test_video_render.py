"""视频 V3 渲染与 files API 测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core.video_constants import VIDEO_ROUTE_PREFIX
from app.models.postgres.shot_asset_model import ShotAssetModel  # noqa: F401
from app.models.postgres.shot_model import ShotModel  # noqa: F401
from app.models.postgres.video_render_job_model import VideoRenderJobModel  # noqa: F401
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_render_client(monkeypatch, tmp_path) -> TestClient:
    """SQLite 内存库 + 临时资产目录的 TestClient。"""
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
    ):
        monkeypatch.setattr(f"{module}.is_postgres_configured", lambda: True)
        monkeypatch.setattr(f"{module}.postgres_session_scope", _scope)

    monkeypatch.setattr(
        "app.video.video_assets_config_reader.load_video_assets_config",
        lambda: type("Cfg", (), {"assets_dir": str(assets_dir)})(),
    )
    return TestClient(create_app())


def _seed_validated_shot(client: TestClient, project_id: str = "demo") -> None:
    """写入并校验一条镜头。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/{project_id}"
    client.post(
        f"{base}/storyboard",
        json={"shots": [{"shot_no": "1", "duration_sec": 3, "action": "推门"}]},
    )
    client.put(
        f"{base}/bible/characters",
        json={"characters": [{"character_id": "c1", "name": "甲"}]},
    )
    client.post(f"{base}/validate")


def test_post_render_creates_assets(pg_render_client: TestClient) -> None:
    """POST render 应产出 Job 与资产记录。"""
    _seed_validated_shot(pg_render_client)
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/render"
    response = pg_render_client.post(url)
    assert response.status_code == 200
    payload = response.json()
    assert payload["job"]["status"] == "completed"
    assert payload["job"]["total_shots"] == 1
    assert len(payload["assets"]) == 2


def test_files_api_serves_keyframe(pg_render_client: TestClient) -> None:
    """files API 应能 inline 打开关键帧。"""
    _seed_validated_shot(pg_render_client)
    render_url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/render"
    assets = pg_render_client.post(render_url).json()["assets"]
    keyframe = next(a for a in assets if a["asset_type"] == "keyframe")
    response = pg_render_client.get(keyframe["open_url"])
    assert response.status_code == 200
    assert "image/svg" in response.headers.get("content-type", "")


def test_get_render_job(pg_render_client: TestClient) -> None:
    """GET jobs 应返回 Job 状态。"""
    _seed_validated_shot(pg_render_client)
    render_url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/render"
    job_id = pg_render_client.post(render_url).json()["job"]["job_id"]
    get_url = f"/api/v1{VIDEO_ROUTE_PREFIX}/jobs/{job_id}"
    response = pg_render_client.get(get_url)
    assert response.status_code == 200
    assert response.json()["finished_shots"] == 1
