"""Ingestion Lite 模块。

【职责】
    内部数据导入：文本切分、embedding、写库适配器、CLI 支撑。
    - dry-run：DryRunFeedAdapter 只预览切分结果
    - 写库：DatabaseFeedAdapter 写 PG documents/chunks + 可选 Neo4j 图谱
"""

from app.ingestion.chunker import chunk_document
from app.ingestion.database_feed_adapter import DatabaseFeedAdapter
from app.ingestion.embedder import HashingEmbedder
from app.ingestion.embedder_factory import build_embedder
from app.ingestion.ingestion_models import IngestionChunk, IngestionDocument, IngestionResult
from app.ingestion.pipeline import run_ingestion_pipeline

__all__ = [
    "DatabaseFeedAdapter",
    "HashingEmbedder",
    "IngestionChunk",
    "IngestionDocument",
    "IngestionResult",
    "build_embedder",
    "chunk_document",
    "run_ingestion_pipeline",
]
