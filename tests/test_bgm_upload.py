"""BGM 上传单元测试。"""

from pathlib import Path

import pytest

from app.services.bgm_upload_service import BgmUploadError, upload_project_bgm
from app.storage.postgres.audio_asset_repository import AudioAssetRepository
from app.video.bgm_filename_validator import validate_bgm_filename


def test_validate_bgm_filename_rejects_bad_ext() -> None:
    """应拒绝非音频扩展名。"""
    with pytest.raises(ValueError):
        validate_bgm_filename("track.txt")


def test_upload_project_bgm_registers_asset(monkeypatch, tmp_path: Path) -> None:
    """上传后应写入 audio_assets。"""
    from app.services import bgm_upload_service as mod

    monkeypatch.setattr(mod, "bgm_storage_dir", lambda _pid: tmp_path / "bgm")
    monkeypatch.setattr(mod, "probe_audio_duration_sec", lambda _p: 12.5)

    class _FakeSession:
        """最小 Session stub。"""

        pass

    class _FakeRepo:
        """内存 Repository。"""

        def __init__(self, _session) -> None:
            self.rows: list[dict] = []

        def delete_bgm_for_project(self, _project_id: str) -> None:
            self.rows.clear()

        def insert_asset(self, project_id, shot_id, track_type, uri, duration_sec, voice_id, source):
            row = {
                "audio_id": "bgm1",
                "project_id": project_id,
                "track_type": track_type,
                "uri": uri,
                "duration_sec": duration_sec,
            }
            self.rows.append(row)

            class _Row:
                audio_id = "bgm1"

            return _Row()

    monkeypatch.setattr(mod, "AudioAssetRepository", _FakeRepo)
    result = upload_project_bgm(_FakeSession(), "demo", "theme.mp3", b"fake-mp3")
    assert result["uri"].endswith("theme.mp3")
    assert result["duration_sec"] == 12.5


def test_upload_empty_raises() -> None:
    """空文件应拒绝。"""
    with pytest.raises(BgmUploadError):
        upload_project_bgm(None, "demo", "a.mp3", b"")
