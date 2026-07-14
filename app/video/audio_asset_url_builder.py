"""音频资产 URL 构造（对白 / BGM 通用）。"""

from app.core.audio_constants import DIALOGUE_WAV_FILENAME


def build_dialogue_open_url(project_id: str, shot_id: str) -> str:
    """对白 WAV inline URL。"""
    base = f"/api/v1/files/video/{project_id}/audio/{shot_id}/{DIALOGUE_WAV_FILENAME}"
    return f"{base}?disposition=inline"


def build_dialogue_download_url(project_id: str, shot_id: str) -> str:
    """对白 WAV 下载 URL。"""
    base = f"/api/v1/files/video/{project_id}/audio/{shot_id}/{DIALOGUE_WAV_FILENAME}"
    return f"{base}?disposition=attachment"


def build_audio_asset_open_url(relative_uri: str) -> str:
    """任意音频相对 URI 的 inline URL。"""
    return f"/api/v1/files/video/{relative_uri}?disposition=inline"


def build_audio_asset_download_url(relative_uri: str) -> str:
    """任意音频相对 URI 的下载 URL。"""
    return f"/api/v1/files/video/{relative_uri}?disposition=attachment"
