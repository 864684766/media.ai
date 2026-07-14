"""创作大纲 API 测试。"""

import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.api.api_constants import CREATIVE_ROUTE_PREFIX
from app.core import constants
from app.core.constants import CHAT_ROUTE_PREFIX
from app.core.creative_plan_constants import PLAN_STATUS_APPROVED, PLAN_STATUS_AWAITING_REVIEW
from app.models.postgres.clarification_session_model import ClarificationSessionModel  # noqa: F401
from app.models.postgres.conversation_model import ConversationModel  # noqa: F401
from app.models.postgres.creative_plan_model import CreativePlanModel  # noqa: F401
from app.models.postgres.message_model import MessageModel  # noqa: F401
from app.models.postgres.time_helper import utc_now
from app.storage.postgres.postgres_metadata import create_all_tables


def _fake_prepare_state(request, repository, retrieval_pipeline=None, route_classifiers=None):
    """跳过真实图，返回最小 state。"""
    from app.graph.state_factory import create_initial_state

    return create_initial_state(request)


def _parse_sse_events(raw: str) -> list[tuple[str, dict]]:
    """解析 SSE 文本。"""
    events: list[tuple[str, dict]] = []
    for block in raw.split("\n\n"):
        if not block.strip():
            continue
        event_name = ""
        data_text = ""
        for line in block.split("\n"):
            if line.startswith("event: "):
                event_name = line[7:].strip()
            if line.startswith("data: "):
                data_text = line[6:]
        if event_name and data_text:
            events.append((event_name, json.loads(data_text)))
    return events


@pytest.fixture()
def pg_creative_client(monkeypatch) -> TestClient:
    """SQLite 内存库 TestClient（澄清 + 大纲）。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_all_tables(engine)
    factory = sessionmaker(bind=engine)
    sessions: list = []

    class _SessionScope:
        """模拟 postgres_session_scope。"""

        def __enter__(self):
            self._session = factory()
            sessions.append(self._session)
            return self._session

        def __exit__(self, *args):
            self._session.close()

    def _scope():
        return _SessionScope()

    monkeypatch.setattr("app.api.deps.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.deps.postgres_session_scope", _scope)
    monkeypatch.setattr("app.api.creative_plans.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.creative_plans.postgres_session_scope", _scope)
    monkeypatch.setattr("app.services.chat_stream_runner.prepare_stream_state", _fake_prepare_state)
    monkeypatch.setattr("app.api.deps.build_retrieval_pipeline", lambda session=None: None)
    client = TestClient(create_app())
    client._test_sessions = sessions  # type: ignore[attr-defined]
    return client


def _complete_clarification(client: TestClient) -> tuple[str, list[tuple[str, dict]]]:
    """走澄清流并返回 (conversation_id, second_round_events)。"""
    url = f"/api/v1{CHAT_ROUTE_PREFIX}"
    first = client.post(
        url,
        json={"message": "想写修仙", "creation_type": "novel", "stream": True},
    )
    events = _parse_sse_events(first.text)
    req = next(data for name, data in events if name == constants.SSE_EVENT_CLARIFICATION_REQUEST)
    session_id = req[constants.SSE_FIELD_CLARIFICATION_SESSION_ID]
    questions = req[constants.SSE_FIELD_CLARIFICATION_QUESTIONS]
    answers = [{"question_id": questions[0]["question_id"], "option_id": questions[0]["options"][0]["option_id"]}]
    second = client.post(
        url,
        json={
            "message": "",
            "creation_type": "novel",
            "stream": True,
            "clarification_response": {"session_id": session_id, "answers": answers},
        },
    )
    second_events = _parse_sse_events(second.text)
    conv = next(
        data[constants.SSE_FIELD_CONVERSATION_ID]
        for name, data in second_events
        if name == constants.SSE_EVENT_MESSAGE_START
    )
    return conv, second_events


def test_clarification_emits_outline_proposed(pg_creative_client: TestClient) -> None:
    """澄清完成后应自动推送 outline_proposed。"""
    conversation_id, second_events = _complete_clarification(pg_creative_client)
    names = [name for name, _ in second_events]
    assert constants.SSE_EVENT_OUTLINE_PROPOSED in names
    listing = pg_creative_client.get(
        f"/api/v1{CREATIVE_ROUTE_PREFIX}/plans",
        params={"conversation_id": conversation_id},
    )
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert len(items) == 1
    assert items[0]["status"] == PLAN_STATUS_AWAITING_REVIEW
    assert "故事梗概" in items[0]["content_md"]


def test_revise_and_approve_plan(pg_creative_client: TestClient) -> None:
    """改稿递增版本，确认后 status=approved。"""
    conversation_id, _ = _complete_clarification(pg_creative_client)
    listing = pg_creative_client.get(
        f"/api/v1{CREATIVE_ROUTE_PREFIX}/plans",
        params={"conversation_id": conversation_id},
    )
    plan_id = listing.json()["items"][0]["plan_id"]
    revised = pg_creative_client.post(
        f"/api/v1{CREATIVE_ROUTE_PREFIX}/plans/{plan_id}/revise",
        json={"comment": "加强第一章冲突"},
    )
    assert revised.status_code == 200
    assert revised.json()["plan"]["version"] == 2
    assert "加强第一章冲突" in revised.json()["plan"]["content_md"]
    approved = pg_creative_client.post(f"/api/v1{CREATIVE_ROUTE_PREFIX}/plans/{plan_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["plan"]["status"] == PLAN_STATUS_APPROVED
    assert approved.json()["plan"]["approved_at"] is not None
