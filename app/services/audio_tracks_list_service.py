"""音频轨列表服务（V8.6）。"""

from sqlalchemy.orm import Session

from app.schemas.video_audio import AudioAssetOutput, AudioTracksListResponse
from app.storage.postgres.audio_asset_repository import AudioAssetRepository
from app.video.audio_asset_url_builder import build_audio_asset_download_url, build_audio_asset_open_url
from app.video.audio_output_url_builder import build_dialogue_download_url, build_dialogue_open_url


def list_project_audio_tracks(session: Session, project_id: str) -> AudioTracksListResponse:
    """列出项目全部 audio_assets。

    参数:
        session: DB Session。
        project_id: 项目 id。

    返回:
        AudioTracksListResponse: 音轨列表。
    """
    rows = AudioAssetRepository(session).list_by_project(project_id)
    items = [_to_output(row) for row in rows]
    return AudioTracksListResponse(project_id=project_id, items=items)


def _to_output(row) -> AudioAssetOutput:
    """ORM 转 API。"""
    if row.shot_id:
        open_url = build_dialogue_open_url(row.project_id, row.shot_id)
        download_url = build_dialogue_download_url(row.project_id, row.shot_id)
    else:
        open_url = build_audio_asset_open_url(row.uri)
        download_url = build_audio_asset_download_url(row.uri)
    return AudioAssetOutput(
        audio_id=row.audio_id,
        shot_id=row.shot_id,
        track_type=row.track_type,
        uri=row.uri,
        duration_sec=row.duration_sec,
        voice_id=row.voice_id,
        open_url=open_url,
        download_url=download_url,
    )
