"""shot_assets Repository。"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.video_constants import ASSET_TYPE_CLIP
from app.models.postgres.shot_asset_model import ShotAssetModel


class ShotAssetRepository:
    """镜头资产读写。"""

    def __init__(self, session: Session) -> None:
        """绑定 Session。"""
        self._session = session

    def insert_asset(
        self,
        shot_id: str,
        project_id: str,
        asset_type: str,
        uri: str,
        last_frame_uri: str = "",
        provider: str = "stub",
        cost: float = 0.0,
    ) -> ShotAssetModel:
        """插入一条资产记录。"""
        row = ShotAssetModel(
            asset_id=uuid.uuid4().hex,
            shot_id=shot_id,
            project_id=project_id,
            asset_type=asset_type,
            uri=uri,
            last_frame_uri=last_frame_uri,
            provider=provider,
            cost=cost,
        )
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return row

    def list_by_project(self, project_id: str) -> list[ShotAssetModel]:
        """列出 project 下资产。"""
        stmt = select(ShotAssetModel).where(ShotAssetModel.project_id == project_id)
        return list(self._session.scalars(stmt).all())

    def find_clip_uri(self, shot_id: str) -> str:
        """查询镜头 clip 资产 URI，无则空串。"""
        stmt = select(ShotAssetModel).where(
            ShotAssetModel.shot_id == shot_id,
            ShotAssetModel.asset_type == ASSET_TYPE_CLIP,
        )
        row = self._session.scalar(stmt)
        return row.uri if row else ""

    def sum_cost_by_project(self, project_id: str) -> float:
        """汇总 project 全部资产 cost。"""
        stmt = select(func.coalesce(func.sum(ShotAssetModel.cost), 0.0)).where(
            ShotAssetModel.project_id == project_id,
        )
        value = self._session.scalar(stmt)
        return float(value or 0.0)
