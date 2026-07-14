"""视频成本 API 测试（V7）。"""

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
from app.video.video_budget_constants import REASON_BUDGET_EXCEEDED


@pytest.fixture()
def pg_cost_client(monkeypatch, tmp_path) -> TestClient:
    """SQLite 内存库 TestClient（含 cost API）。"""
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
        "app.api.video_cost",
    )
    for module in modules:
        monkeypatch.setattr(f"{module}.is_postgres_configured", lambda: True)
        monkeypatch.setattr(f"{module}.postgres_session_scope", _scope)

    monkeypatch.setattr(
        "app.video.video_assets_config_reader.load_video_assets_config",
        lambda: type("Cfg", (), {"assets_dir": str(assets_dir)})(),
    )
    return TestClient(create_app())


def _prepare_validated_shot(client: TestClient) -> None:
    """提交分镜并通过 validate。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo"
    client.post(
        f"{base}/storyboard",
        json={"shots": [{"shot_no": "1", "duration_sec": 5, "scene_id": "s1"}]},
    )
    client.put(f"{base}/bible/scenes", json={"scenes": [{"scene_id": "s1", "name": "A"}]})
    client.post(f"{base}/validate")


def test_cost_api_after_render(pg_cost_client: TestClient, monkeypatch) -> None:
    """渲染后 cost API 应返回非零 cost（stub 为 0）。"""
    monkeypatch.setattr(
        "app.services.render_job_service.load_video_provider_config",
        lambda: type(
            "Cfg",
            (),
            {
                "active_keyframe": "stub",
                "active_clip": "stub",
                "active_compose": "stub_json",
                "matrix": {
                    "stub": type(
                        "Cap",
                        (),
                        {
                            "provider_id": "stub",
                            "cost_per_second": 0.1,
                        },
                    )(),
                },
            },
        )(),
    )
    _prepare_validated_shot(pg_cost_client)
    pg_cost_client.post(f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/render")
    response = pg_cost_client.get(f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/cost")
    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "demo"
    assert body["asset_count"] >= 2
    assert body["total_cost_usd"] == 0.5


def test_budget_fuse_blocks_render(pg_cost_client: TestClient, monkeypatch) -> None:
    """预算过低时 render 应 409。"""
    monkeypatch.setattr(
        "app.video.project_budget_gate.resolve_project_budget_limit_usd",
        lambda session, project_id: 0.01,
    )
    monkeypatch.setattr(
        "app.services.render_job_service.load_video_budget_config",
        lambda: type(
            "Cfg",
            (),
            {"default_limit_usd": 0.01, "fuse_on_render": True, "fuse_on_compose": True},
        )(),
    )
    monkeypatch.setattr(
        "app.services.render_job_service.load_video_provider_config",
        lambda: type(
            "Cfg",
            (),
            {
                "active_keyframe": "stub",
                "active_clip": "stub",
                "active_compose": "stub_json",
                "matrix": {
                    "stub": type("Cap", (), {"provider_id": "stub", "cost_per_second": 1.0})(),
                },
            },
        )(),
    )
    _prepare_validated_shot(pg_cost_client)
    response = pg_cost_client.post(f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/render")
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["reason"] == REASON_BUDGET_EXCEEDED
