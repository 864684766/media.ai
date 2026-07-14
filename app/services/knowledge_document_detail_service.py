"""知识库文档详情服务。"""

from sqlalchemy.orm import Session

from app.schemas.knowledge import KnowledgeDocumentDetailResponse
from app.services.knowledge_delete_service import KnowledgeDocumentNotFoundError
from app.storage.postgres.document_repository import DocumentRepository


def build_document_detail(session: Session, document_id: str) -> KnowledgeDocumentDetailResponse:
    """构建单文档详情响应。

    参数:
        session: DB Session。
        document_id: 文档 id。

    返回:
        KnowledgeDocumentDetailResponse: 详情。

    异常:
        KnowledgeDocumentNotFoundError: 文档不存在。
    """
    row = DocumentRepository(session).get_document(document_id)
    if row is None:
        raise KnowledgeDocumentNotFoundError(document_id)
    chunks = DocumentRepository(session).list_chunks(document_id)
    return KnowledgeDocumentDetailResponse(
        document_id=row.id,
        project_id=row.project_id,
        source=row.source,
        text_length=len(row.text or ""),
        chunk_count=len(chunks),
        created_at=row.created_at.isoformat() if row.created_at else "",
    )
