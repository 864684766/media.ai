"""检索链 × LangGraph × SSE 集成测试。

【覆盖点】
    1. needs_project 问题走 retrieve_context 节点，证据进入 prompt。
    2. 仅创作问题跳过检索节点（retrieval 为 None）。
    3. SSE 流式路径推送 citation 事件（真实数据从 SQLite 灌入）。
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
from app.services.chat_stream_runner import stream_chat_frames
from app.storage.postgres.document_repository import DocumentRepository
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture(autouse=True)
def isolate_neo4j(monkeypatch: pytest.MonkeyPatch) -> None:
    """屏蔽真实 Neo4j：向量路在本测试中不参与（保证跨环境确定性）。"""
    monkeypatch.setattr(
        "app.retrieval.hybrid_factory.create_neo4j_driver",
        lambda: None,
    )


@pytest.fixture()
def seeded_session() -> Session:
    """SQLite 内存库 + 已灌入小说设定数据的 Session。"""
    engine = create_engine("sqlite:///:memory:")
    create_all_tables(engine)
    with Session(engine) as db_session:
        _seed(db_session)
        yield db_session


def _seed(session: Session) -> None:
    """通过 Ingestion 流水线灌入测试设定（走真实写库 adapter）。"""
    adapter = DatabaseFeedAdapter(
        document_repository=DocumentRepository(session),
        chunk_writer=None,
        embedder=HashingEmbedder(16),
    )
    document = IngestionDocument(
        document_id="novel-1",
        project_id="demo",
        source="chapter-1.md",
        text="张三拜青云子为师，青云子将青云剑法倾囊相授。",
    )
    run_ingestion_pipeline(document, adapter=adapter)


def _responder(state) -> str:
    """测试用生成函数。"""
    return "回答"


def test_project_question_retrieves_evidence(seeded_session: Session) -> None:
    """查设定问题应产出检索证据并写进 prompt。"""
    pipeline = build_retrieval_pipeline(seeded_session)
    request = ChatRequest(message="张三的师父是谁", project_id="demo")
    state = run_minimal_chat_graph(request, responder=_responder, retrieval_pipeline=pipeline)
    assert state.retrieval is not None
    assert state.retrieval.chunks
    assert PROMPT_SECTION_EVIDENCE in state.prompt


def test_creative_question_skips_retrieval(seeded_session: Session) -> None:
    """纯创作问题不应触发检索节点。"""
    pipeline = build_retrieval_pipeline(seeded_session)
    request = ChatRequest(message="帮我续写一段山门比试", project_id="demo")
    state = run_minimal_chat_graph(request, responder=_responder, retrieval_pipeline=pipeline)
    assert state.retrieval is None
    assert PROMPT_SECTION_EVIDENCE not in state.prompt


def test_sse_stream_emits_citation_events(
    seeded_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SSE 流式路径应在 message_start 后推送 citation 事件。"""
    # 用假的 Provider delta 流，避免真实调用模型
    monkeypatch.setattr(
        "app.services.chat_stream_runner.yield_provider_delta_frames",
        _fake_delta_frames,
    )
    pipeline = build_retrieval_pipeline(seeded_session)
    request = ChatRequest(message="张三的师父是谁", project_id="demo")
    frames = list(stream_chat_frames(request, repository=None, retrieval_pipeline=pipeline))
    joined = "".join(frames)
    assert "event: citation" in joined
    assert "chunk_id" in joined
    assert "event: message_end" in joined


def _fake_delta_frames(state):
    """假 Provider 流：产出一个 delta 帧并返回完整回答。"""
    yield 'event: content_delta\ndata: {"delta":"答"}\n\n'
    return "答"
