"""Edge TTS 对白生成（V8.5）。

【职责】
    调用 edge-tts 将 shot.dialogue 合成为 WAV。

【何时调用】
    tts_provider_dispatcher 在 tts_provider=edge_tts 时。
"""

import asyncio
from pathlib import Path

import logging

from app.models.postgres.shot_model import ShotModel
from app.video.tts_stub_writer import write_dialogue_wav_stub

logger = logging.getLogger(__name__)


def write_edge_tts_dialogue(
    shot: ShotModel,
    output_path: Path,
    edge_voice: str,
) -> float:
    """用 Edge TTS 写出对白 WAV；失败回退 stub。

    参数:
        shot: 镜头 ORM。
        output_path: 目标路径。
        edge_voice: Edge 音色名。

    返回:
        float: 时长秒。
    """
    text = (shot.dialogue or "").strip()
    if not text:
        return write_dialogue_wav_stub(shot, output_path)
    try:
        return _run_edge_tts(text, edge_voice, output_path, shot)
    except Exception as exc:
        logger.warning("Edge TTS 失败，已降级为静音 stub: %s", exc)
        return write_dialogue_wav_stub(shot, output_path)


def _run_edge_tts(text: str, voice: str, output_path: Path, shot: ShotModel) -> float:
    """同步包装 edge-tts 异步 API。"""
    import edge_tts

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mp3_path = output_path.with_suffix(".mp3")
    asyncio.run(_save_mp3(text, voice, mp3_path, edge_tts))
    duration = _mp3_to_wav(mp3_path, output_path)
    mp3_path.unlink(missing_ok=True)
    return duration or float(shot.duration_sec or 1.0)


async def _save_mp3(text: str, voice: str, mp3_path: Path, edge_tts_module) -> None:
    """异步保存 MP3。"""
    communicate = edge_tts_module.Communicate(text, voice)
    await communicate.save(str(mp3_path))


def _mp3_to_wav(mp3_path: Path, wav_path: Path) -> float:
    """ffmpeg 将 mp3 转 wav。"""
    from app.video.ffmpeg_binary_resolver import resolve_ffmpeg_binary

    binary = resolve_ffmpeg_binary()
    if binary is None:
        raise RuntimeError("ffmpeg required for edge_tts mp3→wav")
    return _ffmpeg_transcode(binary, mp3_path, wav_path)


def _ffmpeg_transcode(binary: str, mp3_path: Path, wav_path: Path) -> float:
    """执行 ffmpeg 转码。"""
    import subprocess

    cmd = [binary, "-y", "-i", str(mp3_path), str(wav_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "mp3 to wav failed")
    return _wav_duration_sec(wav_path)


def _wav_duration_sec(path: Path) -> float:
    """读取 WAV 时长。"""
    import wave

    with wave.open(str(path), "r") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        return frames / float(rate) if rate else 0.0
