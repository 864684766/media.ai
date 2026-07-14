"""BGM 上传服务（V8.6）。"""

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.audio_constants import AUDIO_SOURCE_UPLOAD, TRACK_TYPE_BGM
from app.storage.postgres.audio_asset_repository import AudioAssetRepository
from app.video.bgm_duration_probe import probe_audio_duration_sec
from app.video.bgm_filename_validator import validate_bgm_filename
from app.video.bgm_path_helper import bgm_absolute_path, bgm_relative_uri, bgm_storage_dir


class BgmUploadError(ValueError):
    """BGM 上传校验失败。"""


def upload_project_bgm(session: Session, project_id: str, filename: str, content: bytes) -> dict:
    """保存 BGM 文件并登记 audio_assets（覆盖旧 BGM）。

    参数:
        session: DB Session。
        project_id: 项目 id。
        filename: 原始文件名。
        content: 文件二进制。

    返回:
        dict: 音频资产摘要。
    """
    safe_name = _validate_upload(filename, content)
    target = _write_bgm_file(project_id, safe_name, content)
    return _register_bgm_asset(session, project_id, safe_name, target)


def _validate_upload(filename: str, content: bytes) -> str:
    """校验文件名与内容非空。"""
    if not content:
        raise BgmUploadError("BGM 文件不能为空")
    try:
        return validate_bgm_filename(filename)
    except ValueError as exc:
        raise BgmUploadError(str(exc)) from exc


def _write_bgm_file(project_id: str, safe_name: str, content: bytes) -> Path:
    """落盘 BGM 并返回绝对路径。"""
    folder = bgm_storage_dir(project_id)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / safe_name
    path.write_bytes(content)
    return path


def _register_bgm_asset(session: Session, project_id: str, safe_name: str, path: Path) -> dict:
    """写入 DB 并返回 API 摘要。"""
    repo = AudioAssetRepository(session)
    repo.delete_bgm_for_project(project_id)
    rel = bgm_relative_uri(project_id, safe_name)
    duration = probe_audio_duration_sec(path)
    row = repo.insert_asset(project_id, "", TRACK_TYPE_BGM, rel, duration, "", AUDIO_SOURCE_UPLOAD)
    return {"audio_id": row.audio_id, "uri": rel, "duration_sec": duration}
