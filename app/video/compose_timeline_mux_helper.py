"""从 timeline payload 提取混轨所需字段。"""

from app.core.audio_constants import TRACK_TYPE_DIALOGUE


def extract_mux_inputs(timeline_payload: dict | None) -> tuple[list[dict], list[dict]]:
    """解析 clips 与 dialogue 音轨。

    参数:
        timeline_payload: compose 时间轴 dict。

    返回:
        tuple: (clips, dialogue_tracks)。
    """
    if not timeline_payload:
        return [], []
    clips = timeline_payload.get("clips", [])
    tracks = timeline_payload.get("audio_tracks", [])
    if not isinstance(clips, list) or not isinstance(tracks, list):
        return [], []
    dialogue = [t for t in tracks if t.get("track_type") == TRACK_TYPE_DIALOGUE]
    return clips, dialogue


def has_dialogue_tracks(timeline_payload: dict | None) -> bool:
    """时间轴是否含对白轨。"""
    _, dialogue = extract_mux_inputs(timeline_payload)
    return len(dialogue) > 0
