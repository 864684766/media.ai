"""喂养系统对接 Stub。

【职责】
    提供未来外部喂养系统可以实现的统一接口。

【当前阶段】
    DryRunFeedAdapter 不写 PG / Neo4j，只返回 chunks，便于学习和测试。
"""

from app.ingestion.ingestion_models import IngestionChunk, IngestionDocument, IngestionResult


class DryRunFeedAdapter:
    """dry-run 导入适配器。

    参数说明:
        dry_run: 是否仅预览；当前固定建议 True。
    """

    def __init__(self, dry_run: bool = True) -> None:
        """初始化 dry-run adapter。"""
        self._dry_run = dry_run

    def write_chunks(
        self,
        document: IngestionDocument,
        chunks: list[IngestionChunk],
    ) -> IngestionResult:
        """接收 chunks 并返回导入结果。

        参数:
            document: 原始文档。
            chunks: 切分后的 chunks。

        返回:
            IngestionResult: dry-run 结果。
        """
        return IngestionResult(
            document_id=document.document_id,
            chunk_count=len(chunks),
            dry_run=self._dry_run,
            chunks=chunks,
        )
