"""知识库文档导入服务。"""

from app.core.knowledge_constants import DEFAULT_KNOWLEDGE_SOURCE_PASTE
from app.ingestion.adapter_factory import database_adapter_scope
from app.ingestion.ingestion_models import IngestionDocument, IngestionResult
from app.ingestion.pipeline import run_ingestion_pipeline
from app.schemas.knowledge import KnowledgeIngestResponse


def ingest_text_document(
    project_id: str,
    document_id: str,
    text: str,
    source: str = DEFAULT_KNOWLEDGE_SOURCE_PASTE,
) -> KnowledgeIngestResponse:
    """将纯文本跑 ingestion 流水线并写库。

    参数:
        project_id: 项目 id。
        document_id: 文档 id。
        text: 正文。
        source: 来源标记。

    返回:
        KnowledgeIngestResponse: 导入统计。
    """
    document = _build_document(project_id, document_id, text, source)
    result = _run_write_pipeline(document)
    return _to_response(document, result)


def _build_document(
    project_id: str,
    document_id: str,
    text: str,
    source: str,
) -> IngestionDocument:
    """构造 IngestionDocument。"""
    return IngestionDocument(
        document_id=document_id.strip(),
        project_id=project_id.strip(),
        source=source,
        text=text,
    )


def _run_write_pipeline(document: IngestionDocument) -> IngestionResult:
    """调用 DatabaseFeedAdapter 写库。"""
    with database_adapter_scope() as adapter:
        return run_ingestion_pipeline(document, dry_run=False, adapter=adapter)


def _to_response(document: IngestionDocument, result: IngestionResult) -> KnowledgeIngestResponse:
    """流水线结果转 API 响应。"""
    return KnowledgeIngestResponse(
        document_id=document.document_id,
        project_id=document.project_id,
        chunk_count=result.chunk_count,
        rejected_extensions=[],
    )
