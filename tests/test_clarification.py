"""澄清 SSE 分支测试。"""

import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core import constants
from app.core.constants import CHAT_ROUTE_PREFIX
from app.models.postgres.clarification_session_model import ClarificationSessionModel  # noqa: F401
from app.models.postgres.conversation_model import ConversationModel  # noqa: F401
from app.models.postgres.message_model import MessageModel  # noqa: F401
from app.storage.postgres.postgres_metadata import create_all_tables


def _fake_prepare_state(request, repository, retrieval_pipeline=None, route_classifiers=None):
    """跳过真实图，返回最小 state。"""
    from app.graph.state_factory import create_initial_state

    return create_initial_state(request)


def _parse_sse_events(raw: str) -> list[tuple[str, dict]]:
    """解析 SSE 文本为 (event, data) 列表。"""
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
def pg_clarify_client(monkeypatch) -> TestClient:
    """SQLite 内存库 TestClient（澄清流）。"""
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

    monkeypatch.setattr("app.api.deps.is_postgres_configured", lambda: True)
    monkeypatch.setattr("app.api.deps.postgres_session_scope", _scope)
    monkeypatch.setattr("app.services.chat_stream_runner.prepare_stream_state", _fake_prepare_state)
    monkeypatch.setattr("app.api.deps.build_retrieval_pipeline", lambda session=None: None)
    return TestClient(create_app())


def test_clarification_request_on_novel_brief(pg_clarify_client: TestClient) -> None:
    """模糊小说需求应返回 clarification_request。"""
    url = f"/api/v1{CHAT_ROUTE_PREFIX}"
    response = pg_clarify_client.post(
        url,
        json={"message": "想写修仙", "creation_type": "novel", "stream": True},
    )
    assert response.status_code == 200
    events = _parse_sse_events(response.text)
    names = [name for name, _ in events]
    assert constants.SSE_EVENT_CLARIFICATION_REQUEST in names
    assert constants.SSE_EVENT_CONTENT_DELTA not in names


def test_clarification_response_emits_summary(pg_clarify_client: TestClient) -> None:
    """提交澄清答案后应返回 requirements_summary。"""
    url = f"/api/v1{CHAT_ROUTE_PREFIX}"
    first = pg_clarify_client.post(
        url,
        json={"message": "策划短视频", "creation_type": "video", "stream": True},
    )
    events = _parse_sse_events(first.text)
    req = next(data for name, data in events if name == constants.SSE_EVENT_CLARIFICATION_REQUEST)
    session_id = req[constants.SSE_FIELD_CLARIFICATION_SESSION_ID]
    questions = req[constants.SSE_FIELD_CLARIFICATION_QUESTIONS]
    answers = [
        {
            "question_id": questions[0]["question_id"],
            "option_id": questions[0]["options"][0]["option_id"],
        },
    ]
    second = pg_clarify_client.post(
        url,
        json={
            "message": "",
            "creation_type": "video",
            "stream": True,
            "clarification_response": {"session_id": session_id, "answers": answers},
        },
    )
    names = [name for name, _ in _parse_sse_events(second.text)]
    assert constants.SSE_EVENT_REQUIREMENTS_SUMMARY in names
    assert constants.SSE_EVENT_CLARIFICATION_COMPLETE in names
