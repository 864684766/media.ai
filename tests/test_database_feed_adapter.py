"""DatabaseFeedAdapter 测试（PG 用 SQLite 内存库，Neo4j 用假写入器）。

【覆盖点】
    1. 写 PG：documents 与 chunks 落库，chunk_id 对齐。
    2. Neo4j 写入器收到与 chunk 数量一致的 embedding。
    3. 无 Neo4j（chunk_writer=None）时只写 PG 不报错。
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.ingestion.database_feed_adapter import DatabaseFeedAdapter
from app.ingestion.embedder import HashingEmbedder
from app.ingestion.ingestion_models import IngestionChunk, IngestionDocument
from app.storage.postgres.document_repository import DocumentRepository
from app.storage.postgres.postgres_metadata import create_all_tables


class FakeChunkWriter:
    """记录调用参数的假 Neo4j 写入器。"""

    def __init__(self) -> None:
        """初始化调用记录。"""
        self.calls: list[tuple] = []

    def write_document_chunks(self, document, chunks, embeddings) -> int:
        """记录参数并返回 chunk 数。"""
        self.calls.append((document, chunks, embeddings))
        return len(chunks)


@pytest.fixture()
def session() -> Session:
    """提供 SQLite 内存库 Session。"""
    engine = create_engine("sqlite:///:memory:")
    create_all_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def _document() -> IngestionDocument:
    """构造测试文档。"""
    return IngestionDocument(document_id="doc-9", project_id="demo", source="s", text="全文")


def _chunks() -> list[IngestionChunk]:
    """构造测试 chunks。"""
    return [
        IngestionChunk(chunk_id="doc-9:0", document_id="doc-9", project_id="demo", index=0, text="片段一"),
        IngestionChunk(chunk_id="doc-9:1", document_id="doc-9", project_id="demo", index=1, text="片段二"),
    ]


def test_write_chunks_persists_to_postgres(session: Session) -> None:
    """写库后 PG 应能按序读回 chunks，chunk_id 与输入一致。"""
    repository = DocumentRepository(session)
    adapter = DatabaseFeedAdapter(repository, chunk_writer=None, embedder=HashingEmbedder(16))
    result = adapter.write_chunks(_document(), _chunks())
    assert result.dry_run is False
    stored = repository.list_chunks("doc-9")
    assert [chunk.chunk_id for chunk in stored] == ["doc-9:0", "doc-9:1"]


def test_write_chunks_sends_embeddings_to_neo4j(session: Session) -> None:
    """有 Neo4j 写入器时，embedding 数量应与 chunk 数一致。"""
    writer = FakeChunkWriter()
    adapter = DatabaseFeedAdapter(
        DocumentRepository(session), chunk_writer=writer, embedder=HashingEmbedder(16)
    )
    adapter.write_chunks(_document(), _chunks())
    assert len(writer.calls) == 1
    _, chunks, embeddings = writer.calls[0]
    assert len(embeddings) == len(chunks) == 2
    assert all(len(vector) == 16 for vector in embeddings)
