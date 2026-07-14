"""Neo4j Chunk 写入器。

【职责】
    把 Ingestion 产出的 Document / Chunk（含 embedding）写入 Neo4j：
    (:Document)-[:HAS_CHUNK]->(:Chunk)，相邻 Chunk 之间建 (:Chunk)-[:NEXT]->(:Chunk)。
    对应 docs/ARCHITECTURE.html sec-04.3 图谱模型。

【何时被调用】
    app/ingestion/database_feed_adapter.py 写完 PG 后调用本模块，
    保证 PG 与 Neo4j 使用同一套 chunk_id（sec-04.7）。

【简例】
    writer = Neo4jChunkWriter(driver)
    writer.write_document_chunks(document, chunks, embeddings)
"""

from neo4j import Driver

from app.ingestion.ingestion_models import IngestionChunk, IngestionDocument
from app.storage.neo4j.neo4j_chunk_cypher import (
    MERGE_CHUNK_CYPHER,
    MERGE_DOCUMENT_CYPHER,
    MERGE_NEXT_EDGE_CYPHER,
)
from app.storage.neo4j.neo4j_write_runner import run_write_cypher


class Neo4jChunkWriter:
    """Document / Chunk 图谱写入。

    参数说明:
        driver: Neo4j Driver（由 create_neo4j_driver() 创建）。
    """

    def __init__(self, driver: Driver) -> None:
        """绑定 Driver。"""
        self._driver = driver

    def write_document_chunks(
        self,
        document: IngestionDocument,
        chunks: list[IngestionChunk],
        embeddings: list[list[float]],
    ) -> int:
        """写入文档及其全部 chunks（幂等 MERGE）。

        参数:
            document: 原始文档。
            chunks: 切分后的 chunk 列表（与 embeddings 一一对应）。
            embeddings: 每个 chunk 的向量。

        返回:
            int: 写入的 chunk 数量。
        """
        self._merge_document(document)
        for chunk, embedding in zip(chunks, embeddings):
            self._merge_chunk(chunk, embedding)
        self._link_next_edges(chunks)
        return len(chunks)

    def _merge_document(self, document: IngestionDocument) -> None:
        """MERGE Document 节点。"""
        run_write_cypher(
            MERGE_DOCUMENT_CYPHER,
            {
                "document_id": document.document_id,
                "project_id": document.project_id,
                "source": document.source,
            },
            driver=self._driver,
        )

    def _merge_chunk(self, chunk: IngestionChunk, embedding: list[float]) -> None:
        """MERGE 单个 Chunk 节点并挂 HAS_CHUNK 边。"""
        run_write_cypher(
            MERGE_CHUNK_CYPHER,
            {
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "embedding": embedding,
                "chunk_index": chunk.index,
                "project_id": chunk.project_id,
                "source": chunk.source,
            },
            driver=self._driver,
        )

    def _link_next_edges(self, chunks: list[IngestionChunk]) -> None:
        """相邻 chunk 之间建 NEXT 边（阅读顺序）。"""
        for previous, current in zip(chunks, chunks[1:]):
            run_write_cypher(
                MERGE_NEXT_EDGE_CYPHER,
                {"from_chunk_id": previous.chunk_id, "to_chunk_id": current.chunk_id},
                driver=self._driver,
            )
