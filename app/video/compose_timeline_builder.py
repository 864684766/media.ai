"""时间轴 JSON 构建（纯逻辑）。"""

import json

from app.models.postgres.shot_model import ShotModel


def build_timeline_payload(
    project_id: str,
    job_id: str,
    shots: list[ShotModel],
    clip_uri_by_shot: dict[str, str],
    audio_tracks: list[dict] | None = None,
    subtitle_uri: str = "",
) -> dict:
    """组装 timeline Stub 结构。"""
    clips = [_clip_entry(shot, clip_uri_by_shot) for shot in shots]
    total = sum(item["duration_sec"] for item in clips)
    payload = {
        "project_id": project_id,
        "job_id": job_id,
        "clips": clips,
        "total_duration_sec": total,
    }
    if audio_tracks:
        payload["audio_tracks"] = audio_tracks
    if subtitle_uri:
        payload["subtitle_uri"] = subtitle_uri
    return payload


def timeline_to_json(payload: dict) -> str:
    """时间轴 dict 转 JSON 字符串。"""
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _clip_entry(shot: ShotModel, clip_map: dict[str, str]) -> dict:
    """单镜时间轴条目。"""
    return {
        "shot_id": shot.shot_id,
        "shot_no": shot.shot_no,
        "duration_sec": shot.duration_sec,
        "transition": shot.transition or "",
        "clip_uri": clip_map.get(shot.shot_id, ""),
    }
