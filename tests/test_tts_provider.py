"""TTS Provider 与音画混轨单元测试（V8.5）。"""

from pathlib import Path

import pytest

from app.core.tts_provider_constants import TTS_PROVIDER_EDGE_TTS, TTS_PROVIDER_STUB
from app.video.compose_timeline_mux_helper import has_dialogue_tracks
from app.video.edge_voice_mapper import resolve_edge_voice
from app.video.tts_provider_dispatcher import write_dialogue_wav
from app.video.video_audio_config_reader import VideoAudioConfig


def test_resolve_edge_voice_uses_voice_map() -> None:
    """voice_map 应覆盖 bible voice_id。"""
    mapped = resolve_edge_voice("narrator", "zh-CN-XiaoxiaoNeural", {"narrator": "zh-CN-YunxiNeural"})
    assert mapped == "zh-CN-YunxiNeural"


def test_resolve_edge_voice_uses_bible_id() -> None:
    """已是 Edge 格式的 voice_id 应原样使用。"""
    voice = "zh-CN-YunxiNeural"
    assert resolve_edge_voice(voice, "zh-CN-XiaoxiaoNeural") == voice


def test_resolve_edge_voice_fallback_default() -> None:
    """非 Edge 格式应回退默认音色。"""
    assert resolve_edge_voice("default", "zh-CN-XiaoxiaoNeural") == "zh-CN-XiaoxiaoNeural"


def test_has_dialogue_tracks_detects_payload() -> None:
    """时间轴含 dialogue 轨时应返回 True。"""
    payload = {
        "clips": [{"shot_id": "s1", "duration_sec": 2}],
        "audio_tracks": [{"shot_id": "s1", "track_type": "dialogue", "uri": "a.wav"}],
    }
    assert has_dialogue_tracks(payload) is True
    assert has_dialogue_tracks({"clips": [], "audio_tracks": []}) is False


def test_tts_dispatcher_stub_writes_wav(tmp_path: Path) -> None:
    """stub provider 应写出 WAV 文件。"""
    from app.models.postgres.shot_model import ShotModel

    shot = ShotModel(
        shot_id="sh1",
        project_id="demo",
        shot_no="1",
        duration_sec=1.5,
        dialogue="测试对白",
    )
    cfg = VideoAudioConfig(
        tts_provider=TTS_PROVIDER_STUB,
        edge_default_voice="zh-CN-XiaoxiaoNeural",
        voice_map={},
        bgm_default_volume=0.25,
        bgm_pause_before_compose=True,
        compose_mux_audio=True,
        compose_burn_subtitles=False,
    )
    out = tmp_path / "dialogue.wav"
    duration = write_dialogue_wav(shot, out, "default", cfg)
    assert duration >= 0.5
    assert out.is_file()


def test_tts_dispatcher_edge_config_routes(tmp_path: Path, monkeypatch) -> None:
    """edge_tts 配置应走 edge 写入器（可 mock）。"""
    from app.models.postgres.shot_model import ShotModel

    shot = ShotModel(
        shot_id="sh2",
        project_id="demo",
        shot_no="1",
        duration_sec=2,
        dialogue="你好",
    )
    cfg = VideoAudioConfig(
        tts_provider=TTS_PROVIDER_EDGE_TTS,
        edge_default_voice="zh-CN-XiaoxiaoNeural",
        voice_map={"zh-CN-YunxiNeural": "zh-CN-YunxiNeural"},
        bgm_default_volume=0.25,
        bgm_pause_before_compose=True,
        compose_mux_audio=True,
        compose_burn_subtitles=False,
    )

    def _fake_edge(shot_obj, output_path, edge_voice):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"RIFF")
        return 2.0

    monkeypatch.setattr("app.video.tts_provider_dispatcher.write_edge_tts_dialogue", _fake_edge)
    out = tmp_path / "edge.wav"
    duration = write_dialogue_wav(shot, out, "zh-CN-YunxiNeural", cfg)
    assert duration == 2.0
    assert out.is_file()
