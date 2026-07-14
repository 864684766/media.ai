"""视频分镜 API 测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core.video_constants import VIDEO_ROUTE_PREFIX
from app.models.postgres.shot_model import ShotModel  # noqa: F401 注册 ORM 元数据
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_client(monkeypatch) -> TestClient:
    """使用 SQLite 内存库（StaticPool 共享连接）替换 PG 的 TestClient。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_all_tables(engine)
    factory = sessionmaker(bind=engine)

    class _SessionScope:
        """模拟 postgres_session_scope 上下文管理器。"""

        def __enter__(self):
            self._session = factory()
            return self._session

        def __exit__(self, *args):
            self._session.close()

    def _scope():
        return _SessionScope()

    monkeypatch.setattr("app.api.video.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.video.postgres_session_scope", _scope)
    monkeypatch.setattr("app.api.video_bible.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.video_bible.postgres_session_scope", _scope)
    return TestClient(create_app())


def test_post_storyboard_persists_shots(pg_client: TestClient) -> None:
    """POST storyboard 应返回入库镜头。"""
    body = {
        "shots": [
            {
                "shot_no": "1",
                "duration_sec": 3,
                "action": "推门",
                "character_ids": [],
                "prop_ids": [],
            }
        ]
    }
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/storyboard"
    response = pg_client.post(url, json=body)
    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "demo"
    assert len(payload["shots"]) == 1
    assert payload["shots"][0]["status"] == "draft"


def test_get_shots_lists_by_project(pg_client: TestClient) -> None:
    """GET shots 应返回已提交镜头。"""
    post_url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/storyboard"
    pg_client.post(
        post_url,
        json={"shots": [{"shot_no": "2", "duration_sec": 4, "action": "特写"}]},
    )
    get_url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/shots"
    response = pg_client.get(get_url)
    assert response.status_code == 200
    assert len(response.json()["shots"]) == 1


def test_video_api_503_without_pg(monkeypatch) -> None:
    """未配置 PG 时应返回 503。"""
    monkeypatch.setattr("app.api.video.is_postgres_configured", lambda: False)
    client = TestClient(create_app())
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo/shots"
    response = client.get(url)
    assert response.status_code == 503


def test_validate_entities_api(pg_client: TestClient) -> None:
    """POST validate 应在 bible 齐全时 validated。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo"
    pg_client.post(
        f"{base}/storyboard",
        json={
            "shots": [
                {
                    "shot_no": "1",
                    "duration_sec": 3,
                    "character_ids": ["char_a"],
                    "scene_id": "scene_a",
                }
            ]
        },
    )
    pg_client.put(
        f"{base}/bible/characters",
        json={"characters": [{"character_id": "char_a", "name": "甲"}]},
    )
    pg_client.put(
        f"{base}/bible/scenes",
        json={"scenes": [{"scene_id": "scene_a", "name": "场景"}]},
    )
    response = pg_client.post(f"{base}/validate")
    assert response.status_code == 200
    payload = response.json()
    assert payload["validated_count"] == 1
    assert payload["rejected_count"] == 0
