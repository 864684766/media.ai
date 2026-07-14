"""视频项目 API 测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core.video_constants import VIDEO_ROUTE_PREFIX
from app.models.postgres.video_project_model import VideoProjectModel  # noqa: F401
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_project_client(monkeypatch, tmp_path) -> TestClient:
    """SQLite 内存库 TestClient（项目 CRUD）。"""
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

    monkeypatch.setattr("app.api.video_projects.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.video_projects.postgres_session_scope", _scope)
    monkeypatch.setattr("app.api.video.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.video.postgres_session_scope", _scope)
    return TestClient(create_app())


def test_create_and_list_projects(pg_project_client: TestClient) -> None:
    """POST 创建后 GET 列表应包含该项目。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects"
    create = pg_project_client.post(
        base,
        json={
            "title": "演示短片",
            "project_id": "demo-film",
            "description": "赛博修仙产品宣传片策划",
        },
    )
    assert create.status_code == 200
    body = create.json()
    assert body["project"]["project_id"] == "demo-film"
    assert body["project"]["description"] == "赛博修仙产品宣传片策划"
    listing = pg_project_client.get(base)
    assert listing.status_code == 200
    items = listing.json()["items"]
    match = next(i for i in items if i["project_id"] == "demo-film")
    assert match["description"] == "赛博修仙产品宣传片策划"


def test_suggestions_include_unregistered_namespace(pg_project_client: TestClient) -> None:
    """未建 video_projects 的 shots project_id 应出现在 suggestions。"""
    story = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/legacy-only/storyboard"
    pg_project_client.post(story, json={"shots": [{"shot_no": "1", "duration_sec": 2, "scene_id": "s1"}]})
    url = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/suggestions"
    response = pg_project_client.get(url)
    assert response.status_code == 200
    ids = [item["project_id"] for item in response.json()["items"]]
    assert "legacy-only" in ids
