"""知识库读写 API。"""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.api_constants import DEFAULT_KNOWLEDGE_LIST_LIMIT, KNOWLEDGE_ROUTE_PREFIX
from app.core.knowledge_constants import DEFAULT_KNOWLEDGE_CHUNK_PAGE_SIZE
from app.ingestion.file_text_extractors.extractor_errors import UnsupportedFileExtensionError
from app.schemas.knowledge import (
    KnowledgeChunkListResponse,
    KnowledgeDocumentDetailResponse,
    KnowledgeDocumentListResponse,
    KnowledgeIngestJsonRequest,
    KnowledgeIngestResponse,
)
from app.services.knowledge_chunk_list_service import build_chunk_list_response
from app.services.knowledge_delete_service import (
    KnowledgeDocumentNotFoundError,
    delete_knowledge_document,
)
from app.services.knowledge_document_detail_service import build_document_detail
from app.services.knowledge_ingest_service import ingest_text_document
from app.services.knowledge_list_service import build_knowledge_list_response
from app.services.knowledge_upload_ingest_service import ingest_uploaded_file
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=KNOWLEDGE_ROUTE_PREFIX, tags=["knowledge"])


def _require_postgres() -> None:
    """未配置 DATABASE_URL 时拒绝。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL，无法使用知识库 API")


@router.get("/documents", summary="知识库文档列表")
def list_knowledge_documents(
    project_id: str | None = None,
    limit: int = DEFAULT_KNOWLEDGE_LIST_LIMIT,
) -> KnowledgeDocumentListResponse:
    """返回已导入文档列表（供前端知识库页）。"""
    if not is_postgres_configured():
        return KnowledgeDocumentListResponse(items=[])
    with postgres_session_scope() as session:
        return build_knowledge_list_response(session, project_id=project_id, limit=limit)


@router.post("/documents", summary="导入知识库文档（JSON 文本）", response_model=KnowledgeIngestResponse)
def post_knowledge_document_json(body: KnowledgeIngestJsonRequest) -> KnowledgeIngestResponse:
    """粘贴纯文本或 JSON 提交正文，跑 ingestion 写 PG。"""
    _require_postgres()
    return ingest_text_document(
        body.project_id,
        body.document_id,
        body.text,
        body.source,
    )


@router.post("/documents/upload", summary="导入知识库文档（multipart 文件）", response_model=KnowledgeIngestResponse)
async def post_knowledge_document_upload(
    project_id: str = Form(...),
    document_id: str = Form(...),
    source: str = Form(""),
    file: UploadFile = File(...),
) -> KnowledgeIngestResponse:
    """上传 txt/md/pdf/docx 文件并写库。"""
    _require_postgres()
    try:
        payload = await ingest_uploaded_file(project_id, document_id, file, source)
    except UnsupportedFileExtensionError as exc:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {exc.extension}") from exc
    return KnowledgeIngestResponse.model_validate(payload)


@router.get(
    "/documents/{document_id}",
    summary="知识库文档详情",
    response_model=KnowledgeDocumentDetailResponse,
)
def get_knowledge_document(document_id: str) -> KnowledgeDocumentDetailResponse:
    """返回文档元数据与 chunk 数量。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            return build_document_detail(session, document_id)
    except KnowledgeDocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"文档不存在: {exc.document_id}") from exc


@router.get(
    "/documents/{document_id}/chunks",
    summary="知识库 chunk 分页列表",
    response_model=KnowledgeChunkListResponse,
)
def get_knowledge_document_chunks(
    document_id: str,
    offset: int = 0,
    limit: int = DEFAULT_KNOWLEDGE_CHUNK_PAGE_SIZE,
) -> KnowledgeChunkListResponse:
    """按 index 分页返回 chunk 文本。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            return build_chunk_list_response(session, document_id, offset, limit)
    except KnowledgeDocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"文档不存在: {exc.document_id}") from exc


@router.delete("/documents/{document_id}", summary="删除知识库文档", status_code=204)
def delete_knowledge_document_route(document_id: str) -> None:
    """删除 document 及关联 chunks。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            delete_knowledge_document(session, document_id)
    except KnowledgeDocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"文档不存在: {exc.document_id}") from exc
