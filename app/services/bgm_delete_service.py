"""BGM 删除服务（V8.6）。"""

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.audio_constants import TRACK_TYPE_BGM
from app.storage.postgres.audio_asset_repository import AudioAssetRepository
from app.video.video_assets_config_reader import load_video_assets_config


class BgmNotFoundError(LookupError):
    """BGM 不存在。"""


def delete_project_bgm(session: Session, project_id: str, audio_id: str) -> None:
    """删除 BGM 资产与磁盘文件。

    参数:
        session: DB Session。
        project_id: 项目 id。
        audio_id: 音频 id。

    异常:
        BgmNotFoundError: 记录不存在或类型不匹配。
    """
    repo = AudioAssetRepository(session)
    row = _find_bgm(repo, project_id, audio_id)
    _remove_file(row.uri)
    repo.delete_asset(audio_id)


def _find_bgm(repo: AudioAssetRepository, project_id: str, audio_id: str):
    """查找 BGM 行。"""
    for item in repo.list_by_project(project_id):
        if item.audio_id == audio_id and item.track_type == TRACK_TYPE_BGM:
            return item
    raise BgmNotFoundError(audio_id)


def _remove_file(relative_uri: str) -> None:
    """删除磁盘 BGM 文件（忽略缺失）。"""
    root = Path(load_video_assets_config().assets_dir)
    path = (root / relative_uri).resolve()
    if path.is_file():
        path.unlink()
