"""时间轴对白 WAV 拼接（stdlib wave）。

【职责】
    按镜头顺序将对白 WAV 嵌入时间轴（镜间补静音）。

【何时调用】
    local_ffmpeg_compose_writer 音画混轨前。
"""

import wave
from pathlib import Path

from app.core.audio_constants import TRACK_TYPE_DIALOGUE


def build_timeline_dialogue_wav(
    clips: list[dict],
    audio_tracks: list[dict],
    assets_root: Path,
    output_path: Path,
) -> bool:
    """拼接对白轨为单条 WAV。

    参数:
        clips: timeline clips 列表（含 shot_id、duration_sec）。
        audio_tracks: 音轨元数据（含 shot_id、uri、track_type）。
        assets_root: video.assets_dir 根路径。
        output_path: 输出 WAV 绝对路径。

    返回:
        bool: 是否写出有效对白轨。
    """
    track_map = _dialogue_track_map(audio_tracks)
    if not track_map:
        return False
    segments = _collect_segments(clips, track_map, assets_root)
    if not segments:
        return False
    _write_merged_wav(segments, output_path)
    return True


def _dialogue_track_map(tracks: list[dict]) -> dict[str, str]:
    """shot_id → 对白相对 URI。"""
    result: dict[str, str] = {}
    for row in tracks:
        if row.get("track_type") != TRACK_TYPE_DIALOGUE:
            continue
        shot_id = str(row.get("shot_id", ""))
        uri = str(row.get("uri", ""))
        if shot_id and uri:
            result[shot_id] = uri
    return result


def _collect_segments(clips: list[dict], track_map: dict[str, str], root: Path) -> list[bytes]:
    """按时间轴顺序收集 PCM 帧（含静音）。"""
    rate = 22050
    channels = 1
    width = 2
    timeline: list[bytes] = []
    for clip in clips:
        shot_id = str(clip.get("shot_id", ""))
        duration = float(clip.get("duration_sec") or 1.0)
        uri = track_map.get(shot_id)
        if uri:
            pcm = _read_wav_pcm(root / uri)
            if pcm:
                timeline.append(pcm)
                continue
        silence_frames = int(rate * max(duration, 0.1))
        timeline.append(b"\x00\x00" * silence_frames)
    return timeline


def _read_wav_pcm(path: Path) -> bytes:
    """读取 WAV 原始 PCM。"""
    if not path.is_file():
        return b""
    with wave.open(str(path), "r") as wav_file:
        return wav_file.readframes(wav_file.getnframes())


def _write_merged_wav(segments: list[bytes], output_path: Path) -> None:
    """写出合并 WAV。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 22050
    with wave.open(str(output_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for chunk in segments:
            wav_file.writeframes(chunk)
