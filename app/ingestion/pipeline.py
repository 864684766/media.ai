"""Ingestion Lite 流水线。

【职责】
    编排 文档 → 切分 → feed_adapter 的流程。
    adapter 决定数据去向：
    - DryRunFeedAdapter（默认）：只返回切分结果，不写库
    - DatabaseFeedAdapter：写 PG documents/chunks + 可选 Neo4j 图谱

【何时被调用】
    scripts/seed_novel.py CLI；未来外部喂养系统实现同一 adapter 接口即可接入。
"""

from typing import Protocol

from app.ingestion.chunker import chunk_document
from app.ingestion.feed_adapter import DryRunFeedAdapter
from app.ingestion.ingestion_models import IngestionChunk, IngestionDocument, IngestionResult
from app.ingestion.ingestion_settings import load_ingestion_settings


class FeedAdapter(Protocol):
    """FeedAdapter 统一接口（DryRun 与 Database 两种实现均满足）。"""

    def write_chunks(
        self,
        document: IngestionDocument,
        chunks: list[IngestionChunk],
    ) -> IngestionResult:
        """接收切分结果并返回导入结果。"""
        ...


def run_ingestion_pipeline(
    document: IngestionDocument,
    dry_run: bool | None = None,
    adapter: FeedAdapter | None = None,
) -> IngestionResult:
    """执行 Ingestion Lite 流水线。

    参数:
        document: 待导入文档。
        dry_run: 是否 dry-run；None 时读取 config/app.yaml；传入 adapter 时忽略。
        adapter: 可选写库适配器；None 时用 DryRunFeedAdapter。

    返回:
        IngestionResult: 导入结果。
    """
    settings = load_ingestion_settings()
    chunks = chunk_document(
        document,
        chunk_size=int(settings["chunk_size"]),
        chunk_overlap=int(settings["chunk_overlap"]),
    )
    if adapter is None:
        adapter = DryRunFeedAdapter(dry_run=_resolve_dry_run(settings, dry_run))
    return adapter.write_chunks(document, chunks)


def _resolve_dry_run(settings: dict[str, int | bool], dry_run: bool | None) -> bool:
    """解析 dry_run 最终值。"""
    if dry_run is not None:
        return dry_run
    value = settings["dry_run_default"]
    return value if isinstance(value, bool) else True
