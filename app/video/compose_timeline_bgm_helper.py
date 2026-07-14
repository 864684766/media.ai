"""从 timeline payload 提取 BGM 音轨。"""

from app.core.audio_constants import TRACK_TYPE_BGM


def extract_bgm_track(timeline_payload: dict | None) -> dict | None:
    """返回第一条 BGM 轨元数据。

    参数:
        timeline_payload: compose 时间轴 dict。

    返回:
        dict | None: 含 uri、volume 等；无 BGM 时 None。
    """
    if not timeline_payload:
        return None
    tracks = timeline_payload.get("audio_tracks", [])
    if not isinstance(tracks, list):
        return None
    for row in tracks:
        if row.get("track_type") == TRACK_TYPE_BGM:
            uri = str(row.get("uri", "")).strip()
            if uri:
                return row
    return None
