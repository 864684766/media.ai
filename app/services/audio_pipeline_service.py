"""音频流水线业务服务（V8）。"""

from sqlalchemy.orm import Session

from app.core.audio_constants import AUDIO_SOURCE_TTS, TRACK_TYPE_DIALOGUE
from app.schemas.video_audio import AudioAssetOutput, AudioPipelineResponse
from app.storage.postgres.audio_asset_repository import AudioAssetRepository
from app.storage.postgres.shot_repository import ShotRepository
from app.video.audio_output_path_helper import (
    dialogue_relative_uri,
    dialogue_wav_path,
    subtitle_relative_uri,
    subtitle_srt_path,
)
from app.video.audio_output_url_builder import build_dialogue_download_url, build_dialogue_open_url
from app.video.compose_output_url_builder import build_compose_open_url
from app.video.shot_voice_id_resolver import resolve_shot_voice_id
from app.video.subtitle_srt_builder import build_srt_content
from app.video.tts_provider_dispatcher import write_dialogue_wav
from app.video.video_audio_config_reader import load_video_audio_config


def run_audio_pipeline(session: Session, project_id: str) -> AudioPipelineResponse:
    """为含对白镜头生成 TTS Stub 与 SRT 字幕。

    参数:
        session: DB Session。
        project_id: 项目 id。

    返回:
        AudioPipelineResponse: 产出摘要。
    """
    shots = ShotRepository(session).list_by_project(project_id)
    dialogue_shots = [s for s in shots if (s.dialogue or "").strip()]
    assets = _generate_dialogue_assets(session, dialogue_shots)
    subtitle_uri = _write_subtitle_file(project_id, shots)
    return _build_response(project_id, assets, subtitle_uri)


def _generate_dialogue_assets(session, shots) -> list[AudioAssetOutput]:
    """逐镜写出对白 WAV 并入库。"""
    repo = AudioAssetRepository(session)
    outputs: list[AudioAssetOutput] = []
    for shot in shots:
        outputs.append(_one_dialogue_asset(session, repo, shot))
    return outputs


def _one_dialogue_asset(session, repo, shot) -> AudioAssetOutput:
    """生成单镜对白资产。"""
    path = dialogue_wav_path(shot.project_id, shot.shot_id)
    voice_id = resolve_shot_voice_id(session, shot)
    audio_cfg = load_video_audio_config()
    duration = write_dialogue_wav(shot, path, voice_id, audio_cfg)
    rel = dialogue_relative_uri(shot.project_id, shot.shot_id)
    row = repo.insert_asset(
        shot.project_id, shot.shot_id, TRACK_TYPE_DIALOGUE, rel, duration, voice_id, AUDIO_SOURCE_TTS,
    )
    return _asset_output(row)


def _write_subtitle_file(project_id: str, shots) -> str:
    """写出 SRT 并返回相对 URI。"""
    path = subtitle_srt_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_srt_content(shots), encoding="utf-8")
    return subtitle_relative_uri(project_id)


def _asset_output(row) -> AudioAssetOutput:
    """ORM 转 API 输出。"""
    return AudioAssetOutput(
        audio_id=row.audio_id,
        shot_id=row.shot_id,
        track_type=row.track_type,
        uri=row.uri,
        duration_sec=row.duration_sec,
        voice_id=row.voice_id,
        open_url=build_dialogue_open_url(row.project_id, row.shot_id),
        download_url=build_dialogue_download_url(row.project_id, row.shot_id),
    )


def _build_response(project_id, assets, subtitle_uri) -> AudioPipelineResponse:
    """组装 POST audio 响应。"""
    return AudioPipelineResponse(
        project_id=project_id,
        dialogue_count=len(assets),
        subtitle_uri=subtitle_uri,
        subtitle_open_url=build_compose_open_url(subtitle_uri),
        assets=assets,
        tts_provider=load_video_audio_config().tts_provider,
    )
