"""消息 TXT 产物下载 API。"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.api_constants import CONVERSATIONS_ROUTE_PREFIX
from app.core.artifact_constants import (
    ARTIFACT_DOWNLOAD_SEGMENT,
    ARTIFACT_ROUTE_SEGMENT,
    NOVEL_ARTIFACT_MIME,
)
from app.services.message_artifact_service import (
    resolve_assistant_txt_path,
    save_assistant_txt_artifact,
)
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=CONVERSATIONS_ROUTE_PREFIX, tags=["conversations"])


def _load_artifact_path(conversation_id: str, message_id: int) -> Path:
    """从 PG 生成或读取 TXT 路径。

    异常:
        HTTPException: 404 消息不存在。
    """
    with postgres_session_scope() as session:
        repo = ConversationRepository(session)
        saved = save_assistant_txt_artifact(repo, conversation_id, message_id)
        if saved is None:
            raise HTTPException(status_code=404, detail="消息不存在")
        return saved


@router.get(
    "/{conversation_id}/messages/{message_id}/" + ARTIFACT_ROUTE_SEGMENT,
    summary="浏览器打开小说 TXT",
)
def open_message_artifact(conversation_id: str, message_id: int) -> FileResponse:
    """inline 方式返回 text/plain，供新标签页打开。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")
    path = _load_artifact_path(conversation_id, message_id)
    filename = resolve_assistant_txt_path(conversation_id, message_id).name
    return FileResponse(
        path,
        media_type=NOVEL_ARTIFACT_MIME,
        filename=filename,
        content_disposition_type="inline",
    )


@router.get(
    "/{conversation_id}/messages/{message_id}/" + ARTIFACT_DOWNLOAD_SEGMENT,
    summary="下载小说 TXT",
)
def download_message_artifact(conversation_id: str, message_id: int) -> FileResponse:
    """attachment 方式下载 TXT。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")
    path = _load_artifact_path(conversation_id, message_id)
    filename = resolve_assistant_txt_path(conversation_id, message_id).name
    return FileResponse(
        path,
        media_type=NOVEL_ARTIFACT_MIME,
        filename=filename,
        content_disposition_type="attachment",
    )
