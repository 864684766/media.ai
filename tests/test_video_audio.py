"""视频音频流水线测试（V8）。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core.video_constants import VIDEO_ROUTE_PREFIX
from app.models.postgres.audio_asset_model import AudioAssetModel  # noqa: F401
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_audio_client(monkeypatch, tmp_path) -> TestClient:
    """SQLite + 资产目录 TestClient。"""
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

    for module in ("app.api.video", "app.api.video_audio"):
        monkeypatch.setattr(f"{module}.is_postgres_configured", lambda: True)
        monkeypatch.setattr(f"{module}.postgres_session_scope", _scope)

    monkeypatch.setattr(
        "app.video.video_assets_config_reader.load_video_assets_config",
        lambda: type("Cfg", (), {"assets_dir": str(assets_dir)})(),
    )
    return TestClient(create_app())


def test_audio_pipeline_writes_dialogue_and_subtitle(pg_audio_client: TestClient) -> None:
    """POST audio 应对白镜头生成资产与 SRT。"""
    base = f"/api/v1{VIDEO_ROUTE_PREFIX}/projects/demo-audio"
    pg_audio_client.post(
        f"{base}/storyboard",
        json={
            "shots": [
                {
                    "shot_no": "1",
                    "duration_sec": 2,
                    "dialogue": "你好，山门。",
                    "scene_id": "s1",
                },
            ],
        },
    )
    response = pg_audio_client.post(f"{base}/audio")
    assert response.status_code == 200
    body = response.json()
    assert body["dialogue_count"] == 1
    assert body["subtitle_uri"].endswith("subtitles.srt")
    assert len(body["assets"]) == 1
