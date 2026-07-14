"""TTS Provider 分发（V8.5）。

【职责】
    按 video.audio.tts_provider 选择 stub 或 edge_tts 写出对白 WAV。

【何时调用】
    audio_pipeline_service 逐镜生成对白前。
"""

from pathlib import Path

from app.core.tts_provider_constants import TTS_PROVIDER_EDGE_TTS
from app.models.postgres.shot_model import ShotModel
from app.video.edge_tts_dialogue_writer import write_edge_tts_dialogue
from app.video.edge_voice_mapper import resolve_edge_voice
from app.video.tts_stub_writer import write_dialogue_wav_stub
from app.video.video_audio_config_reader import VideoAudioConfig


def write_dialogue_wav(
    shot: ShotModel,
    output_path: Path,
    voice_id: str,
    config: VideoAudioConfig,
) -> float:
    """按配置写出对白 WAV。

    参数:
        shot: 镜头 ORM。
        output_path: 目标绝对路径。
        voice_id: character_bible 解析的 voice_id。
        config: 音频配置。

    返回:
        float: 时长秒。
    """
    if config.tts_provider == TTS_PROVIDER_EDGE_TTS:
        edge_voice = resolve_edge_voice(voice_id, config.edge_default_voice, config.voice_map)
        return write_edge_tts_dialogue(shot, output_path, edge_voice)
    return write_dialogue_wav_stub(shot, output_path)
