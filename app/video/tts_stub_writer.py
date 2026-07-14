"""TTS 对白 Stub：生成静音 WAV（V8）。

【职责】
    无真实 TTS Provider 时写出占位 WAV，时长对齐 shot.duration_sec。

【何时调用】
    audio_pipeline_service 逐镜生成对白轨。
"""

import wave
from pathlib import Path

from app.models.postgres.shot_model import ShotModel


def write_dialogue_wav_stub(shot: ShotModel, output_path: Path) -> float:
    """写出静音 WAV 并返回时长。

    参数:
        shot: 镜头 ORM。
        output_path: 目标绝对路径。

    返回:
        float: 时长秒。
    """
    duration = max(float(shot.duration_sec or 1.0), 0.5)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_silent_wav(output_path, duration)
    return duration


def _write_silent_wav(path: Path, duration_sec: float) -> None:
    """用标准库 wave 写静音 PCM。"""
    sample_rate = 22050
    frames = int(sample_rate * duration_sec)
    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frames)
