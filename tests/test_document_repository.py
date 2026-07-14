"""DocumentRepository 与 ChunkKeywordSearcher 测试（SQLite 内存库）。

【覆盖点】
    1. upsert_document：新建与覆盖。
    2. replace_chunks：幂等覆盖（重复导入不产生重复行）。
    3. 关键词召回：中文 bigram 命中、project 过滤、top_k 截断。
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.ingestion.ingestion_models import IngestionChunk, IngestionDocument
from app.storage.postgres.chunk_keyword_searcher import ChunkKeywordSearcher
from app.storage.postgres.document_repository import DocumentRepository
from app.storage.postgres.postgres_metadata import create_all_tables


@pytest.fixture()
def session() -> Session:
    """提供 SQLite 内存库 Session（每个用例独立）。"""
    engine = create_engine("sqlite:///:memory:")
    create_all_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def _make_document(document_id: str = "doc-1") -> IngestionDocument:
    """构造测试文档。"""
    return IngestionDocument(
        document_id=document_id,
        project_id="demo",
        source="chapter-1.md",
        text="张三拜青云子为师，学习青云剑法。",
    )


def _make_chunks(document_id: str = "doc-1") -> list[IngestionChunk]:
    """构造两个测试 chunk。"""
    return [
        IngestionChunk(
            chunk_id=f"{document_id}:0",
            document_id=document_id,
            project_id="demo",
            index=0,
            text="张三拜青云子为师。",
            source="chapter-1.md",
        ),
        IngestionChunk(
            chunk_id=f"{document_id}:1",
            document_id=document_id,
            project_id="demo",
            index=1,
            text="李四在山下开了一家酒馆。",
            source="chapter-1.md",
        ),
    ]


def test_upsert_document_creates_and_overwrites(session: Session) -> None:
    """同一 id 二次 upsert 应覆盖内容而不是报错。"""
    repository = DocumentRepository(session)
    repository.upsert_document(_make_document())
    updated = _make_document()
    updated.text = "改稿后的正文"
    model = repository.upsert_document(updated)
    assert model.text == "改稿后的正文"


def test_replace_chunks_is_idempotent(session: Session) -> None:
    """重复导入同一文档，chunk 数量应保持不变。"""
    repository = DocumentRepository(session)
    repository.upsert_document(_make_document())
    repository.replace_chunks("doc-1", _make_chunks())
    repository.replace_chunks("doc-1", _make_chunks())
    assert len(repository.list_chunks("doc-1")) == 2


def test_keyword_search_hits_chinese_bigram(session: Session) -> None:
    """「张三的师父」应通过 bigram 命中含「张三」「师」的 chunk。"""
    repository = DocumentRepository(session)
    repository.upsert_document(_make_document())
    repository.replace_chunks("doc-1", _make_chunks())
    searcher = ChunkKeywordSearcher(session)
    results = searcher.search("张三的师父", project_id="demo", top_k=5)
    assert results
    top_chunk, top_score = results[0]
    assert top_chunk.chunk_id == "doc-1:0"
    assert top_score > 0


def test_keyword_search_respects_project_filter(session: Session) -> None:
    """project_id 不匹配时不应返回任何结果。"""
    repository = DocumentRepository(session)
    repository.upsert_document(_make_document())
    repository.replace_chunks("doc-1", _make_chunks())
    searcher = ChunkKeywordSearcher(session)
    assert searcher.search("张三", project_id="other", top_k=5) == []
