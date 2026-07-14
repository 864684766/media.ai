"""Chat 接口测试。"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_postgres_repository, get_retrieval_pipeline
from app.application import app
from app.core import constants
from app.core.config import settings
from app.core.constants import CHAT_ROUTE_PREFIX
from app.graph.route_classifiers import RouteClassifiers
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.postgres_metadata import create_all_tables
from tests.sse_parse_helper import extract_conversation_id, extract_event_names

client = TestClient(app)


def test_chat_post_sse_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证 POST /chat 返回标准 SSE 事件流。

    断言:
        - HTTP 200
        - 含 status(thinking) → message_start → content_delta → message_end
    """
    monkeypatch.setattr(settings, "zhipu_api_key", None)
    _apply_chat_test_overrides(repository=None)
    try:
        response = client.post(_build_chat_url(), json={"message": "你好", "stream": True})
        assert response.status_code == 200
        names = extract_event_names(response.text)
        assert constants.SSE_EVENT_STATUS in names
        assert constants.SSE_EVENT_MESSAGE_START in names
        assert constants.SSE_EVENT_CONTENT_DELTA in names
        assert constants.SSE_EVENT_MESSAGE_END in names
        status_data = next(
            data for name, data in _parse_for_status(response.text) if name == constants.SSE_EVENT_STATUS
        )
        assert status_data[constants.SSE_FIELD_STATUS_PHASE] == constants.STATUS_PHASE_THINKING
    finally:
        app.dependency_overrides.clear()


def test_chat_post_sse_persists_with_repository_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """覆盖 Repository 后 POST /chat 应持久化 user+assistant 两条消息。"""
    monkeypatch.setattr(settings, "zhipu_api_key", None)
    repository = _build_test_repository()
    _apply_chat_test_overrides(repository=repository)
    try:
        response = client.post(_build_chat_url(), json={"message": "需要落库", "stream": True})
        conversation_id = extract_conversation_id(response.text)
        messages = repository.list_messages(conversation_id)
        assert response.status_code == 200
        assert len(messages) == 2
    finally:
        app.dependency_overrides.clear()


def _apply_chat_test_overrides(repository: ConversationRepository | None) -> None:
    """注入测试用依赖，跳过 Neo4j/LLM 路由以稳定契约。"""
    def _repo_override() -> Iterator[ConversationRepository | None]:
        yield repository

    def _pipeline_override() -> Iterator[RetrievalPipeline]:
        from app.retrieval.hybrid_factory import build_retrieval_pipeline

        yield build_retrieval_pipeline(session=None)

    app.dependency_overrides[get_postgres_repository] = _repo_override
    app.dependency_overrides[get_retrieval_pipeline] = _pipeline_override
    app.dependency_overrides[_route_classifiers_dep()] = lambda: RouteClassifiers(
        semantic=None,
        llm=None,
    )


def _route_classifiers_dep():
    """延迟 import 避免循环依赖。"""
    from app.api.deps import get_route_classifiers

    return get_route_classifiers


def _parse_for_status(raw: str) -> list[tuple[str, dict]]:
    """复用 sse_parse_helper（本文件内薄封装）。"""
    from tests.sse_parse_helper import parse_sse_events

    return parse_sse_events(raw)


def _build_chat_url() -> str:
    """构造 chat 接口完整路径。"""
    return f"{settings.api_prefix}{CHAT_ROUTE_PREFIX}"


def _build_test_repository() -> ConversationRepository:
    """创建测试用 SQLite Repository。"""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_all_tables(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return ConversationRepository(factory())
