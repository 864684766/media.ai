"""真实写库 FeedAdapter（PG + 可选 Neo4j）。

【职责】
    实现与 DryRunFeedAdapter 相同的 write_chunks 接口，把切分结果真正写入：
    1. PostgreSQL documents / chunks 表（真相源）
    2. Neo4j Document / Chunk 节点 + 向量（可选；未配置时跳过并提示）
    对应 docs/ARCHITECTURE.html sec-13 Phase 2「切分 → embedding → 写 PG + Neo4j」。

【Chunk ID 对齐】
    PG chunks.chunk_id 与 Neo4j :Chunk.id 使用同一值（sec-04.7），
    这是 Hybrid RRF 融合与 citation 回指的前提。

【简例】
    adapter = DatabaseFeedAdapter(document_repository, chunk_writer, embedder)
    result = adapter.write_chunks(document, chunks)
"""

from app.ingestion.embedder import Embedder
from app.ingestion.ingestion_models import IngestionChunk, IngestionDocument, IngestionResult
from app.storage.neo4j.neo4j_chunk_writer import Neo4jChunkWriter
from app.storage.postgres.document_repository import DocumentRepository


class DatabaseFeedAdapter:
    """真实写库导入适配器。

    参数说明:
        document_repository: PG 文档/chunk Repository（必需，真相源）。
        chunk_writer: Neo4j 写入器；None 时只写 PG（无 Neo4j 环境也可用）。
        embedder: 向量化器；写 Neo4j 时为 chunk 生成 embedding。
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_writer: Neo4jChunkWriter | None,
        embedder: Embedder,
    ) -> None:
        """绑定依赖。"""
        self._document_repository = document_repository
        self._chunk_writer = chunk_writer
        self._embedder = embedder

    def write_chunks(
        self,
        document: IngestionDocument,
        chunks: list[IngestionChunk],
    ) -> IngestionResult:
        """把文档与 chunks 写入 PG（及可选 Neo4j）。

        参数:
            document: 原始文档。
            chunks: 切分后的 chunks。

        返回:
            IngestionResult: dry_run=False 的导入结果。
        """
        # 步骤 1：写 PG（真相源），同一文档重复导入时覆盖旧 chunks
        self._document_repository.upsert_document(document)
        self._document_repository.replace_chunks(document.document_id, chunks)
        # 步骤 2：写 Neo4j（派生索引），未配置时跳过
        if self._chunk_writer is not None:
            self._write_neo4j(document, chunks)
        return IngestionResult(
            document_id=document.document_id,
            chunk_count=len(chunks),
            dry_run=False,
            chunks=chunks,
        )

    def _write_neo4j(
        self,
        document: IngestionDocument,
        chunks: list[IngestionChunk],
    ) -> None:
        """生成 embedding 并写入 Neo4j 图谱。"""
        embeddings = self._embedder.embed_texts([chunk.text for chunk in chunks])
        self._chunk_writer.write_document_chunks(document, chunks, embeddings)
