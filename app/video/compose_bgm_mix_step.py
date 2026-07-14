"""合成后 BGM 混轨步骤。"""

import tempfile
from pathlib import Path

from app.video.compose_timeline_bgm_helper import extract_bgm_track
from app.video.local_ffmpeg_bgm_muxer import mix_bgm_into_video
from app.video.video_assets_config_reader import load_video_assets_config
from app.video.video_audio_config_reader import load_video_audio_config


def maybe_mix_bgm_into_output(
    binary: str,
    project_id: str,
    output_path: Path,
    timeline_payload: dict | None,
) -> None:
    """若时间轴含 BGM 则混入成片 mp4。

    参数:
        binary: ffmpeg 路径。
        project_id: 项目 id（未使用，保留扩展）。
        output_path: 成片 mp4 绝对路径。
        timeline_payload: 时间轴 JSON。
    """
    _ = project_id
    bgm_track = extract_bgm_track(timeline_payload)
    if bgm_track is None:
        return
    root = Path(load_video_assets_config().assets_dir)
    bgm_path = (root / str(bgm_track.get("uri", ""))).resolve()
    if not bgm_path.is_file():
        return
    volume = _resolve_bgm_volume(bgm_track)
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        staged = Path(tmp.name)
    try:
        mix_bgm_into_video(binary, output_path, bgm_path, staged, volume)
        staged.replace(output_path)
    finally:
        staged.unlink(missing_ok=True)


def _resolve_bgm_volume(track: dict) -> float:
    """优先轨 metadata，否则 app.yaml 默认。"""
    raw = track.get("volume")
    if raw is not None:
        return float(raw)
    return load_video_audio_config().bgm_default_volume
