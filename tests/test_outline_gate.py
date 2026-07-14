"""大纲闸门测试（阶段 G）。"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application import create_app
from app.core import constants
from app.core.constants import CHAT_ROUTE_PREFIX
from app.core.creative_plan_constants import PLAN_STATUS_AWAITING_REVIEW
from app.core.outline_gate_constants import OUTLINE_GATE_BLOCK_MESSAGE
from app.creative.outline_gate_detector import should_enforce_outline_gate
from app.core.creative_config_reader import OutlineConfig
from app.graph.state_factory import create_initial_state
from app.models.postgres.clarification_session_model import ClarificationSessionModel  # noqa: F401
from app.models.postgres.conversation_model import ConversationModel  # noqa: F401
from app.models.postgres.creative_plan_model import CreativePlanModel  # noqa: F401
from app.models.postgres.message_model import MessageModel  # noqa: F401
from app.models.postgres.time_helper import utc_now
from app.schemas.agent_state import RouteDecision
from app.schemas.chat import ChatRequest
from app.services.outline_gate_stream_service import try_outline_gate_stream
from app.storage.postgres.postgres_metadata import create_all_tables
from tests.sse_parse_helper import extract_event_names, parse_sse_events


def _fake_prepare_state(request, repository, retrieval_pipeline=None, route_classifiers=None):
    """跳过真实图，返回最小 state。"""
    return create_initial_state(request)


@pytest.fixture()
def pg_gate_client(monkeypatch) -> TestClient:
    """SQLite TestClient（大纲闸门）。"""
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


def test_should_enforce_exempts_setting_query() -> None:
    """设定查询豁免闸门。"""
    req = ChatRequest(message="张三的师父是谁", creation_type="novel")
    state = create_initial_state(req).model_copy(
        update={"route": RouteDecision(needs_project=True, needs_creative=False)},
    )
    cfg = OutlineConfig(enabled=True, requires_clarification=True, auto_approve=False, max_revisions=10)
    assert should_enforce_outline_gate(req, state, cfg) is False


def test_try_outline_gate_blocks_when_plan_not_approved() -> None:
    """有 awaiting_review 大纲时应拦截。"""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    create_all_tables(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    conv_id = str(uuid4())
    session.add(
        CreativePlanModel(
            plan_id=str(uuid4()),
            conversation_id=conv_id,
            project_id=None,
            creation_type="novel",
            status=PLAN_STATUS_AWAITING_REVIEW,
            version=1,
            title="纲要",
            content_json="{}",
            content_md="## 第一章",
            created_at=utc_now(),
            updated_at=utc_now(),
        ),
    )
    session.commit()
    req = ChatRequest(message="开始写正文", creation_type="novel", conversation_id=conv_id)
    state = create_initial_state(req)
    outcome = try_outline_gate_stream(req, state, session)
    assert outcome is not None
    assert OUTLINE_GATE_BLOCK_MESSAGE in outcome.frames[0]


def test_outline_gate_blocks_chat_after_clarification(pg_gate_client: TestClient) -> None:
    """澄清+大纲后未 approve，续写应被闸门拦截。"""
    url = f"/api/v1{CHAT_ROUTE_PREFIX}"
    first = pg_gate_client.post(
        url,
        json={"message": "想写修仙长篇", "creation_type": "novel", "stream": True},
    )
    events = parse_sse_events(first.text)
    conv = next(
        d[constants.SSE_FIELD_CONVERSATION_ID]
        for n, d in events
        if n == constants.SSE_EVENT_MESSAGE_START
    )
    if constants.SSE_EVENT_CLARIFICATION_REQUEST in [n for n, _ in events]:
        req = next(d for n, d in events if n == constants.SSE_EVENT_CLARIFICATION_REQUEST)
        q = req[constants.SSE_FIELD_CLARIFICATION_QUESTIONS][0]
        pg_gate_client.post(
            url,
            json={
                "message": "",
                "creation_type": "novel",
                "conversation_id": conv,
                "stream": True,
                "clarification_response": {
                    "session_id": req[constants.SSE_FIELD_CLARIFICATION_SESSION_ID],
                    "answers": [{"question_id": q["question_id"], "option_id": q["options"][0]["option_id"]}],
                },
            },
        )
    second = pg_gate_client.post(
        url,
        json={
            "message": "开始写第一章正文",
            "creation_type": "novel",
            "conversation_id": conv,
            "stream": True,
        },
    )
    assert second.status_code == 200
    assert OUTLINE_GATE_BLOCK_MESSAGE in second.text
    assert constants.SSE_EVENT_CONTENT_DELTA in extract_event_names(second.text)
