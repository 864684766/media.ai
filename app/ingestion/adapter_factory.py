"""FeedAdapter 工厂。

【职责】
    按 .env 与 config/app.yaml 组装真实写库的 DatabaseFeedAdapter：
    - PG Session（DATABASE_URL 必须已配置，否则报错）
    - Neo4j 写入器（可选；未配置 NEO4J_URI 时跳过并只写 PG）
    - Embedder（ingestion.embedding 配置）
    并在有 Neo4j 时确保向量索引已创建。

【何时被调用】
    scripts/seed_novel.py 的 --write 模式。

【简例】
    with database_adapter_scope() as adapter:
        run_ingestion_pipeline(document, adapter=adapter)
"""

from collections.abc import Iterator
from contextlib import contextmanager

from app.ingestion import ingestion_constants as ic
from app.ingestion.database_feed_adapter import DatabaseFeedAdapter
from app.ingestion.embedder import Embedder
from app.ingestion.embedder_factory import build_embedder
from app.ingestion.ingestion_settings import load_embedding_settings
from app.storage.neo4j.neo4j_chunk_writer import Neo4jChunkWriter
from app.storage.neo4j.neo4j_driver_factory import create_neo4j_driver
from app.storage.neo4j.neo4j_vector_index import ensure_chunk_vector_index
from app.storage.postgres.document_repository import DocumentRepository
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


@contextmanager
def database_adapter_scope() -> Iterator[DatabaseFeedAdapter]:
    """创建真实写库 adapter 的上下文（自动管理 PG Session 生命周期）。

    yields:
        DatabaseFeedAdapter: 已组装好 PG / Neo4j / Embedder 的适配器。

    异常:
        RuntimeError: 未配置 DATABASE_URL 时抛出（PG 是真相源，必须有）。
    """
    if not is_postgres_configured():
        raise RuntimeError("写库模式需要配置 .env 的 DATABASE_URL（PG 是真相源）")
    embedder = _build_configured_embedder()
    chunk_writer = _build_optional_chunk_writer(embedder)
    with postgres_session_scope() as session:
        yield DatabaseFeedAdapter(
            document_repository=DocumentRepository(session),
            chunk_writer=chunk_writer,
            embedder=embedder,
        )


def _build_configured_embedder() -> Embedder:
    """按 config/app.yaml ingestion.embedding 构造 Embedder。"""
    settings = load_embedding_settings()
    return build_embedder(
        provider=str(settings[ic.YAML_KEY_EMBEDDING_PROVIDER]),
        dimension=int(settings[ic.YAML_KEY_EMBEDDING_DIMENSION]),
    )


def _build_optional_chunk_writer(embedder: Embedder) -> Neo4jChunkWriter | None:
    """有 Neo4j 配置时构造写入器并确保向量索引存在；否则返回 None。"""
    driver = create_neo4j_driver()
    if driver is None:
        return None
    ensure_chunk_vector_index(driver, dimension=embedder.dimension)
    return Neo4jChunkWriter(driver)
