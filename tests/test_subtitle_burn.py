"""字幕烧录单元测试（阶段 G3）。"""

from pathlib import Path

from app.video.subtitle_burn_eligibility import (
    resolve_subtitles_burned_flag,
    should_burn_subtitles_for_project,
)
from app.video.subtitle_filter_path_escaper import escape_path_for_subtitles_filter
from app.video.video_audio_config_reader import VideoAudioConfig


def test_escape_path_for_subtitles_filter_windows_style() -> None:
    """路径转义应使用正斜杠并转义冒号。"""
    raw = Path("E:/demo/proj/compose/subtitles.srt")
    escaped = escape_path_for_subtitles_filter(raw)
    assert escaped.startswith("'")
    assert "\\:" in escaped or ":" not in escaped[1:-1]


def test_should_burn_when_config_and_srt_exist(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """配置开启且 SRT 存在时应烧录。"""
    project_id = "demo-proj"
    srt = tmp_path / project_id / "compose" / "subtitles.srt"
    srt.parent.mkdir(parents=True)
    srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nhi\n", encoding="utf-8")

    cfg = VideoAudioConfig(
        tts_provider="stub",
        edge_default_voice="zh-CN-XiaoxiaoNeural",
        voice_map={},
        bgm_default_volume=0.25,
        bgm_pause_before_compose=False,
        compose_mux_audio=True,
        compose_burn_subtitles=True,
    )
    monkeypatch.setattr(
        "app.video.subtitle_burn_eligibility.load_video_audio_config",
        lambda: cfg,
    )
    monkeypatch.setattr(
        "app.video.subtitle_burn_eligibility.subtitle_srt_path",
        lambda _pid: srt,
    )
    uri = f"{project_id}/compose/timeline.mp4"
    assert should_burn_subtitles_for_project(project_id, uri) is True
    assert resolve_subtitles_burned_flag(project_id, uri) is True


def test_should_not_burn_without_srt(monkeypatch, tmp_path: Path) -> None:
    """无 SRT 时不应标记烧录。"""
    cfg = VideoAudioConfig(
        tts_provider="stub",
        edge_default_voice="zh-CN-XiaoxiaoNeural",
        voice_map={},
        bgm_default_volume=0.25,
        bgm_pause_before_compose=False,
        compose_mux_audio=True,
        compose_burn_subtitles=True,
    )
    monkeypatch.setattr(
        "app.video.subtitle_burn_eligibility.load_video_audio_config",
        lambda: cfg,
    )
    missing = tmp_path / "missing.srt"
    monkeypatch.setattr(
        "app.video.subtitle_burn_eligibility.subtitle_srt_path",
        lambda _pid: missing,
    )
    assert should_burn_subtitles_for_project("p1", "p1/compose/timeline.mp4") is False
