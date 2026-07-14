"""ffmpeg 可用性校验单元测试。"""

import pytest

from app.video.ffmpeg_required_checker import FfmpegRequiredError, assert_ffmpeg_for_compose
from app.video.video_provider_config_reader import VideoProviderConfig


def test_compose_requires_mp4_clips(monkeypatch) -> None:
    """local_ffmpeg 合成需 mp4 clip。"""
    monkeypatch.setattr(
        "app.video.ffmpeg_required_checker.is_ffmpeg_available",
        lambda: True,
    )
    cfg = VideoProviderConfig(
        active_keyframe="stub",
        active_clip="local_ffmpeg",
        active_compose="local_ffmpeg",
        matrix={},
    )
    with pytest.raises(FfmpegRequiredError, match="mp4"):
        assert_ffmpeg_for_compose(cfg, ["demo/s1/clip.stub.txt"])
