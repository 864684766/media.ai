"""多轮对话 × 持久化 × 检索 综合集成测试。

【场景还原】
    第 1 轮：用户续写请求（仅创作，不检索），消息落库。
    第 2 轮：同一会话查设定（needs_project），应带上第 1 轮历史 + 检索证据。

【验证目标】
    1. conversation_id 串联两轮，第 2 轮 history 含第 1 轮消息。
    2. 第 2 轮触发检索并把证据拼进 prompt。
    3. 两轮消息全部持久化（4 条：user/assistant × 2）。
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.graph.chat_graph import run_minimal_chat_graph
from app.graph.prompt_constants import PROMPT_SECTION_EVIDENCE
from app.ingestion.database_feed_adapter import DatabaseFeedAdapter
from app.ingestion.embedder import HashingEmbedder
from app.ingestion.ingestion_models import IngestionDocument
from app.ingestion.pipeline import run_ingestion_pipeline
from app.retrieval.hybrid_factory import build_retrieval_pipeline
from app.schemas.chat import ChatRequest
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.document_repository import DocumentRepository
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture(autouse=True)
def isolate_neo4j(monkeypatch: pytest.MonkeyPatch) -> None:
    """屏蔽真实 Neo4j，保证测试跨环境确定性。"""
    monkeypatch.setattr(
        "app.retrieval.hybrid_factory.create_neo4j_driver",
        lambda: None,
    )


@pytest.fixture()
def session() -> Session:
    """SQLite 内存库 Session（会话表 + 文档表齐全）。"""
    engine = create_engine("sqlite:///:memory:")
    create_all_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def _seed_novel(session: Session) -> None:
    """灌入小说设定供第 2 轮检索。"""
    adapter = DatabaseFeedAdapter(
        document_repository=DocumentRepository(session),
        chunk_writer=None,
        embedder=HashingEmbedder(16),
    )
    document = IngestionDocument(
        document_id="novel-x",
        project_id="demo",
        source="chapter-1.md",
        text="张三拜青云子为师，青云子传授他青云剑法第一式。",
    )
    run_ingestion_pipeline(document, adapter=adapter)


def _responder(state) -> str:
    """测试用生成函数：回显是否见到了证据。"""
    if PROMPT_SECTION_EVIDENCE in state.prompt:
        return "根据设定，张三的师父是青云子。"
    return "好的，这是续写内容。"


def test_two_turn_conversation_with_retrieval(session: Session) -> None:
    """两轮对话：第 1 轮创作落库，第 2 轮续聊 + 检索。"""
    _seed_novel(session)
    repository = ConversationRepository(session)
    pipeline = build_retrieval_pipeline(session)

    # 第 1 轮：仅创作
    first = run_minimal_chat_graph(
        ChatRequest(message="帮我续写一段山门比试", project_id="demo"),
        responder=_responder,
        repository=repository,
        retrieval_pipeline=pipeline,
    )
    assert first.retrieval is None
    assert first.answer == "好的，这是续写内容。"

    # 第 2 轮：同一会话查设定
    second = run_minimal_chat_graph(
        ChatRequest(
            message="张三的师父是谁",
            conversation_id=first.conversation_id,
            project_id="demo",
        ),
        responder=_responder,
        repository=repository,
        retrieval_pipeline=pipeline,
    )
    # 历史应包含第 1 轮的 user + assistant
    history_contents = [message.content for message in second.history]
    assert "帮我续写一段山门比试" in history_contents
    # 检索证据生效
    assert second.retrieval is not None and second.retrieval.chunks
    assert second.answer == "根据设定，张三的师父是青云子。"
    # 两轮共 4 条消息落库
    stored = repository.list_messages(first.conversation_id)
    assert len(stored) == 4
