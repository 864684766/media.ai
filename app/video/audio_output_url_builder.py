"""音频文件 URL 构造（V8）。"""

from app.video.audio_asset_url_builder import (
    build_audio_asset_download_url,
    build_audio_asset_open_url,
    build_dialogue_download_url,
    build_dialogue_open_url,
)

__all__ = [
    "build_dialogue_open_url",
    "build_dialogue_download_url",
    "build_audio_asset_open_url",
    "build_audio_asset_download_url",
]
