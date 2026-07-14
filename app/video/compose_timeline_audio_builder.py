"""时间轴音轨条目构建（V8）。"""

from app.core.audio_constants import TRACK_TYPE_BGM
from app.models.postgres.audio_asset_model import AudioAssetModel
from app.video.video_audio_config_reader import load_video_audio_config


def build_audio_track_entries(assets: list[AudioAssetModel]) -> list[dict]:
    """将 audio_assets 转为 timeline JSON 音轨列表。"""
    return [_track_dict(row) for row in assets]


def _track_dict(row: AudioAssetModel) -> dict:
    """单条音轨摘要。"""
    entry = {
        "audio_id": row.audio_id,
        "shot_id": row.shot_id,
        "track_type": row.track_type,
        "uri": row.uri,
        "duration_sec": row.duration_sec,
        "voice_id": row.voice_id,
    }
    if row.track_type == TRACK_TYPE_BGM:
        entry["volume"] = load_video_audio_config().bgm_default_volume
    return entry
