"""镜头资产 ORM。"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class ShotAssetModel(Base):
    """shot_assets 表。"""

    __tablename__ = pc.TABLE_SHOT_ASSETS

    asset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    shot_id: Mapped[str] = mapped_column(String(64), index=True)
    project_id: Mapped[str] = mapped_column(String(64), index=True)
    asset_type: Mapped[str] = mapped_column(String(32))
    uri: Mapped[str] = mapped_column(String(512), default="")
    last_frame_uri: Mapped[str] = mapped_column(String(512), default="")
    provider: Mapped[str] = mapped_column(String(64), default="stub")
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    take_no: Mapped[int] = mapped_column(Integer, default=1)
    selected: Mapped[int] = mapped_column(Integer, default=1)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
