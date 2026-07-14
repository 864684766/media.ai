"""音频产物路径辅助（V8）。"""

from pathlib import Path

from app.core.audio_constants import DIALOGUE_WAV_FILENAME, SUBTITLE_SRT_FILENAME
from app.video.video_assets_config_reader import load_video_assets_config


def dialogue_wav_path(project_id: str, shot_id: str) -> Path:
    """单镜对白 WAV 绝对路径。"""
    root = Path(load_video_assets_config().assets_dir)
    return root / project_id / "audio" / shot_id / DIALOGUE_WAV_FILENAME


def subtitle_srt_path(project_id: str) -> Path:
    """项目字幕 SRT 绝对路径。"""
    root = Path(load_video_assets_config().assets_dir)
    return root / project_id / "compose" / SUBTITLE_SRT_FILENAME


def dialogue_relative_uri(project_id: str, shot_id: str) -> str:
    """对白 files API 相对路径。"""
    return f"{project_id}/audio/{shot_id}/{DIALOGUE_WAV_FILENAME}"


def subtitle_relative_uri(project_id: str) -> str:
    """字幕 files API 相对路径。"""
    return f"{project_id}/compose/{SUBTITLE_SRT_FILENAME}"
