"""GET /conversations 与 /skills API 测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.application import app
from app.services.conversation_list_service import build_conversation_list_response
from app.services.conversation_messages_service import build_message_list_response
from app.storage.postgres import postgres_constants as pc
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.postgres_metadata import create_all_tables

client = TestClient(app)


@pytest.fixture()
def session() -> Session:
    """SQLite 内存库 Session。"""
    engine = create_engine("sqlite:///:memory:")
    create_all_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def test_list_skills_returns_registered_skills() -> None:
    """GET /api/v1/skills 应返回至少 novel-writing。"""
    response = client.get("/api/v1/skills")
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["items"]]
    assert "novel-writing" in ids


def test_list_conversations_empty_without_pg(monkeypatch: pytest.MonkeyPatch) -> None:
    """未配置 PG 时会话列表为空。"""
    monkeypatch.setattr(
        "app.api.conversations.is_postgres_configured",
        lambda: False,
    )
    response = client.get("/api/v1/conversations")
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_list_conversations_with_data(session: Session) -> None:
    """服务层应返回会话及 preview、creation_type。"""
    repo = ConversationRepository(session)
    repo.create_conversation("conv-1", project_id="demo", creation_type="video")
    repo.append_message("conv-1", pc.MESSAGE_ROLE_USER, "你好世界")
    response = build_conversation_list_response(session)
    assert len(response.items) == 1
    assert response.items[0].id == "conv-1"
    assert response.items[0].creation_type == "video"
    assert "你好" in response.items[0].preview


def test_list_messages_includes_creation_type(session: Session) -> None:
    """消息列表应携带会话 creation_type。"""
    repo = ConversationRepository(session)
    repo.create_conversation("conv-3", creation_type="video")
    repo.append_message("conv-3", pc.MESSAGE_ROLE_USER, "视频需求")
    response = build_message_list_response(repo, "conv-3")
    assert response is not None
    assert response.creation_type == "video"


def test_list_messages_service(session: Session) -> None:
    """服务层应返回历史消息。"""
    repo = ConversationRepository(session)
    repo.create_conversation("conv-2")
    repo.append_message("conv-2", pc.MESSAGE_ROLE_USER, "问题")
    repo.append_message("conv-2", pc.MESSAGE_ROLE_ASSISTANT, "回答")
    response = build_message_list_response(repo, "conv-2")
    assert response is not None
    assert len(response.items) == 2
    assert response.items[0].role == pc.MESSAGE_ROLE_USER


def test_list_messages_404_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """未配置 PG 时拉历史应 404。"""
    monkeypatch.setattr("app.api.deps.is_postgres_configured", lambda: False)
    response = client.get("/api/v1/conversations/missing/messages")
    assert response.status_code == 404
