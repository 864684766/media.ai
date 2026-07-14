"""知识库 multipart 上传解析。"""

from fastapi import UploadFile

from app.core.knowledge_constants import DEFAULT_KNOWLEDGE_SOURCE_UPLOAD
from app.ingestion.file_text_extractors.extract_upload_text import extract_text_from_upload
from app.services.knowledge_ingest_service import ingest_text_document


async def ingest_uploaded_file(
    project_id: str,
    document_id: str,
    upload: UploadFile,
    source: str = "",
) -> dict:
    """解析 multipart 文件并导入。

    参数:
        project_id: 项目 id。
        document_id: 文档 id。
        upload: FastAPI 上传文件。
        source: 可选来源；缺省用文件名。

    返回:
        dict: KnowledgeIngestResponse 字段。
    """
    raw = await upload.read()
    filename = upload.filename or document_id
    text = extract_text_from_upload(filename, raw)
    resolved_source = source.strip() or filename or DEFAULT_KNOWLEDGE_SOURCE_UPLOAD
    response = ingest_text_document(project_id, document_id, text, resolved_source)
    return response.model_dump()
