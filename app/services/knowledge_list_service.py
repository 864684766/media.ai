"""知识库列表服务。"""

from sqlalchemy.orm import Session

from app.schemas.knowledge import KnowledgeDocumentItem, KnowledgeDocumentListResponse
from app.storage.postgres.document_list_query import query_documents
from app.storage.postgres.document_repository import DocumentRepository

PREVIEW_MAX_CHARS = 120


def build_knowledge_list_response(
    session: Session,
    project_id: str | None = None,
    limit: int = 50,
) -> KnowledgeDocumentListResponse:
    """构建知识库文档列表响应。"""
    rows = query_documents(session, project_id, limit)
    items = [_to_item(session, row) for row in rows]
    return KnowledgeDocumentListResponse(items=items)


def _to_item(session: Session, row) -> KnowledgeDocumentItem:
    """ORM 转 API 条目。"""
    repo = DocumentRepository(session)
    chunks = repo.list_chunks(row.id)
    preview = row.text[:PREVIEW_MAX_CHARS]
    return KnowledgeDocumentItem(
        document_id=row.id,
        project_id=row.project_id,
        source=row.source,
        preview=preview,
        chunk_count=len(chunks),
    )
