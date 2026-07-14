"""视频 BGM 与音轨 API（V8.6）。"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_audio import AudioTracksListResponse, BgmUploadResponse
from app.services.audio_tracks_list_service import list_project_audio_tracks
from app.services.bgm_delete_service import BgmNotFoundError, delete_project_bgm
from app.services.bgm_upload_service import BgmUploadError, upload_project_bgm
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured
from app.video.audio_asset_url_builder import build_audio_asset_download_url, build_audio_asset_open_url
from app.video.ffmpeg_required_checker import FfmpegRequiredError

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 PG 时 503。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")


@router.get(
    "/projects/{project_id}/audio/tracks",
    summary="列出项目音频轨",
    response_model=AudioTracksListResponse,
)
def get_audio_tracks(project_id: str) -> AudioTracksListResponse:
    """返回对白 / BGM / 音效登记列表。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return list_project_audio_tracks(session, project_id)


@router.post(
    "/projects/{project_id}/audio/bgm",
    summary="上传项目 BGM",
    response_model=BgmUploadResponse,
)
async def post_project_bgm(project_id: str, file: UploadFile = File(...)) -> BgmUploadResponse:
    """上传 mp3/wav 等作为全片 BGM（覆盖旧 BGM）。"""
    _require_postgres()
    content = await file.read()
    try:
        with postgres_session_scope() as session:
            result = upload_project_bgm(session, project_id, file.filename or "bgm.mp3", content)
    except BgmUploadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FfmpegRequiredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    rel = str(result["uri"])
    return BgmUploadResponse(
        project_id=project_id,
        audio_id=str(result["audio_id"]),
        uri=rel,
        duration_sec=float(result["duration_sec"]),
        open_url=build_audio_asset_open_url(rel),
        download_url=build_audio_asset_download_url(rel),
    )


@router.delete(
    "/projects/{project_id}/audio/bgm/{audio_id}",
    summary="删除项目 BGM",
    status_code=204,
)
def delete_project_bgm_route(project_id: str, audio_id: str) -> None:
    """删除 BGM 登记与磁盘文件。"""
    _require_postgres()
    try:
        with postgres_session_scope() as session:
            delete_project_bgm(session, project_id, audio_id)
    except BgmNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"BGM 不存在: {exc}") from exc
