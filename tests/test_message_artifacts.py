"""小说 TXT artifact API 测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core.artifact_constants import ARTIFACT_DOWNLOAD_SEGMENT, ARTIFACT_ROUTE_SEGMENT
from app.models.postgres.conversation_model import ConversationModel  # noqa: F401
from app.models.postgres.message_model import MessageModel  # noqa: F401
from app.storage.postgres import postgres_constants as pc
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def pg_artifact_client(monkeypatch, tmp_path) -> TestClient:
    """带会话消息与 artifact 目录的 TestClient。"""
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

    novel_dir = tmp_path / "novel"
    novel_dir.mkdir()
    monkeypatch.setattr(
        "app.api.message_artifacts.is_postgres_configured",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.api.message_artifacts.postgres_session_scope",
        _scope,
    )
    monkeypatch.setattr(
        "app.storage.local.artifact_config_reader.load_artifact_config",
        lambda: type("Cfg", (), {"novel_dir": str(novel_dir)})(),
    )
    client = TestClient(create_app())
    with _scope() as session:
        from app.storage.postgres.conversation_repository import ConversationRepository

        repo = ConversationRepository(session)
        repo.create_conversation("conv-1", "demo")
        repo.append_message("conv-1", pc.MESSAGE_ROLE_ASSISTANT, "第一章 开端")
    return client


def test_open_message_artifact(pg_artifact_client: TestClient) -> None:
    """GET artifact 应 inline 返回 TXT。"""
    url = (
        "/api/v1/conversations/conv-1/messages/1/"
        f"{ARTIFACT_ROUTE_SEGMENT}"
    )
    response = pg_artifact_client.get(url)
    assert response.status_code == 200
    assert "第一章" in response.text


def test_download_message_artifact(pg_artifact_client: TestClient) -> None:
    """GET artifact/download 应 attachment 下载。"""
    url = (
        "/api/v1/conversations/conv-1/messages/1/"
        f"{ARTIFACT_DOWNLOAD_SEGMENT}"
    )
    response = pg_artifact_client.get(url)
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")
