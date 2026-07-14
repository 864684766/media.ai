"""最小 Chat 图单元测试。"""

from app.graph import run_minimal_chat_graph
from app.graph.graph_constants import (
    MEMORY_MESSAGE_ID_ASSISTANT,
    MEMORY_MESSAGE_ID_USER,
)
from app.schemas.agent_state import AgentState
from app.schemas.chat import ChatRequest
from app.storage.postgres import postgres_constants as pc
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.postgres_metadata import create_all_tables
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import pytest

from app.core.config import settings


def test_minimal_chat_graph_runs_all_nodes() -> None:
    """最小图应写入 skill、route、prompt、answer、message_ids。"""
    request = ChatRequest(message="帮我续写一段打斗", skill_id="novel-writing")
    state = run_minimal_chat_graph(request, responder=_fake_responder)
    assert state.skill is not None
    assert state.skill.id == "novel-writing"
    assert state.route is not None
    assert state.route.needs_creative is True
    assert "资深玄幻小说作家" in state.prompt
    assert state.answer == "假模型回复"
    assert state.message_ids == [MEMORY_MESSAGE_ID_USER, MEMORY_MESSAGE_ID_ASSISTANT]


def test_minimal_chat_graph_creates_conversation_id() -> None:
    """请求不带 conversation_id 时，图应自动生成一个 id。"""
    request = ChatRequest(message="你好")
    state = run_minimal_chat_graph(request, responder=_fake_responder)
    assert state.conversation_id
    assert state.thread_id == state.conversation_id


def test_minimal_chat_graph_loads_history_from_repository() -> None:
    """注入 Repository 时，load_history 应读取旧消息。"""
    repository = _build_repository()
    repository.create_conversation("c-history")
    repository.append_message("c-history", pc.MESSAGE_ROLE_USER, "上一轮")
    request = ChatRequest(message="继续", conversation_id="c-history")
    state = run_minimal_chat_graph(request, responder=_fake_responder, repository=repository)
    assert state.history[0].content == "上一轮"


def test_minimal_chat_graph_saves_messages_to_repository() -> None:
    """注入 Repository 时，save_messages 应保存 user/assistant。"""
    repository = _build_repository()
    request = ChatRequest(message="保存这一轮", conversation_id="c-save")
    state = run_minimal_chat_graph(request, responder=_fake_responder, repository=repository)
    messages = repository.list_messages("c-save")
    assert len(messages) == 2
    assert state.message_ids == ["1", "2"]


def test_minimal_chat_graph_default_provider_without_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """未配置 API Key 时，默认生成返回可读提示而不是异常。"""
    monkeypatch.setattr(settings, "zhipu_api_key", None)
    request = ChatRequest(message="你好")
    state = run_minimal_chat_graph(request)
    assert "未配置 API Key" in state.answer


def _fake_responder(state: AgentState) -> str:
    """测试用生成函数，不调用真实 Provider。"""
    assert state.prompt
    return "假模型回复"


def _build_repository() -> ConversationRepository:
    """创建 SQLite 内存库 Repository。"""
    session = _open_test_session()
    return ConversationRepository(session)


def _open_test_session() -> Session:
    """创建 SQLite 内存库 Session。"""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    create_all_tables(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return factory()
