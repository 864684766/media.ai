"""audio_assets Repository（V8）。"""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.audio_constants import TRACK_TYPE_BGM, TRACK_TYPE_DIALOGUE
from app.models.postgres.audio_asset_model import AudioAssetModel


class AudioAssetRepository:
    """音频资产读写。"""

    def __init__(self, session: Session) -> None:
        """绑定 Session。"""
        self._session = session

    def insert_asset(
        self,
        project_id: str,
        shot_id: str,
        track_type: str,
        uri: str,
        duration_sec: float,
        voice_id: str,
        source: str,
    ) -> AudioAssetModel:
        """插入一条音频资产。"""
        row = AudioAssetModel(
            audio_id=uuid.uuid4().hex,
            project_id=project_id,
            shot_id=shot_id,
            track_type=track_type,
            uri=uri,
            duration_sec=duration_sec,
            voice_id=voice_id,
            source=source,
        )
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return row

    def list_by_project(self, project_id: str) -> list[AudioAssetModel]:
        """列出 project 下全部音频资产。"""
        stmt = select(AudioAssetModel).where(AudioAssetModel.project_id == project_id)
        return list(self._session.scalars(stmt).all())

    def find_dialogue_by_shot(self, shot_id: str) -> AudioAssetModel | None:
        """查询镜头对白轨。"""
        stmt = select(AudioAssetModel).where(
            AudioAssetModel.shot_id == shot_id,
            AudioAssetModel.track_type == TRACK_TYPE_DIALOGUE,
        )
        return self._session.scalar(stmt)

    def find_bgm_by_project(self, project_id: str) -> AudioAssetModel | None:
        """查询项目 BGM 轨（单条）。"""
        stmt = select(AudioAssetModel).where(
            AudioAssetModel.project_id == project_id,
            AudioAssetModel.track_type == TRACK_TYPE_BGM,
        )
        return self._session.scalar(stmt)

    def delete_asset(self, audio_id: str) -> bool:
        """按 id 删除音频资产。"""
        stmt = delete(AudioAssetModel).where(AudioAssetModel.audio_id == audio_id)
        result = self._session.execute(stmt)
        self._session.commit()
        return result.rowcount > 0

    def delete_bgm_for_project(self, project_id: str) -> None:
        """删除项目全部 BGM 轨。"""
        stmt = delete(AudioAssetModel).where(
            AudioAssetModel.project_id == project_id,
            AudioAssetModel.track_type == TRACK_TYPE_BGM,
        )
        self._session.execute(stmt)
        self._session.commit()
