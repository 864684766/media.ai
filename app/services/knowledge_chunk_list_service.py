"""知识库 chunk 分页列表服务。"""

from sqlalchemy.orm import Session

from app.core.knowledge_constants import (
    DEFAULT_KNOWLEDGE_CHUNK_PAGE_SIZE,
    MAX_KNOWLEDGE_CHUNK_PAGE_SIZE,
)
from app.schemas.knowledge import KnowledgeChunkItem, KnowledgeChunkListResponse
from app.services.knowledge_delete_service import KnowledgeDocumentNotFoundError
from app.storage.postgres.document_repository import DocumentRepository


def build_chunk_list_response(
    session: Session,
    document_id: str,
    offset: int = 0,
    limit: int = DEFAULT_KNOWLEDGE_CHUNK_PAGE_SIZE,
) -> KnowledgeChunkListResponse:
    """构建 chunk 分页响应。

    参数:
        session: DB Session。
        document_id: 文档 id。
        offset: 偏移。
        limit: 每页条数。

    返回:
        KnowledgeChunkListResponse: 分页结果。

    异常:
        KnowledgeDocumentNotFoundError: 文档不存在。
    """
    repo = DocumentRepository(session)
    if repo.get_document(document_id) is None:
        raise KnowledgeDocumentNotFoundError(document_id)
    page_limit = _clamp_limit(limit)
    rows = repo.list_chunks(document_id)
    page = rows[offset : offset + page_limit]
    items = [_to_item(row) for row in page]
    return KnowledgeChunkListResponse(
        document_id=document_id,
        total=len(rows),
        offset=offset,
        limit=page_limit,
        items=items,
    )


def _clamp_limit(limit: int) -> int:
    """限制分页上限。"""
    safe = max(1, limit)
    return min(safe, MAX_KNOWLEDGE_CHUNK_PAGE_SIZE)


def _to_item(row) -> KnowledgeChunkItem:
    """ORM chunk 转 API 条目。"""
    return KnowledgeChunkItem(
        chunk_id=row.chunk_id,
        chunk_index=row.chunk_index,
        text=row.text,
    )
