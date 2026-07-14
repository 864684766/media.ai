"""视频音频流水线 API（V8）。"""

from fastapi import APIRouter, HTTPException

from app.api.api_constants import VIDEO_ROUTE_PREFIX
from app.schemas.video_audio import AudioPipelineResponse
from app.services.audio_pipeline_service import run_audio_pipeline
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured

router = APIRouter(prefix=VIDEO_ROUTE_PREFIX, tags=["video"])


def _require_postgres() -> None:
    """未配置 PG 时 503。"""
    if not is_postgres_configured():
        raise HTTPException(status_code=503, detail="未配置 DATABASE_URL")


@router.post(
    "/projects/{project_id}/audio",
    summary="生成对白 TTS 与字幕",
    response_model=AudioPipelineResponse,
)
def post_audio_pipeline(project_id: str) -> AudioPipelineResponse:
    """扫描含 dialogue 的镜头，写出 WAV Stub 与 subtitles.srt。"""
    _require_postgres()
    with postgres_session_scope() as session:
        return run_audio_pipeline(session, project_id)
