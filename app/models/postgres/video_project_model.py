"""视频项目 ORM（video_projects 表）。"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.video_project_constants import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_PROJECT_FPS,
    DEFAULT_RESOLUTION,
    DEFAULT_TARGET_DURATION_SEC,
    PROJECT_STATUS_ACTIVE,
)
from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class VideoProjectModel(Base):
    """视频项目元数据表。"""

    __tablename__ = pc.TABLE_VIDEO_PROJECTS

    project_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(256), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    target_duration_sec: Mapped[float] = mapped_column(Float, default=DEFAULT_TARGET_DURATION_SEC)
    aspect_ratio: Mapped[str] = mapped_column(String(16), default=DEFAULT_ASPECT_RATIO)
    resolution: Mapped[str] = mapped_column(String(32), default=DEFAULT_RESOLUTION)
    fps: Mapped[int] = mapped_column(Integer, default=DEFAULT_PROJECT_FPS)
    style_bible: Mapped[str] = mapped_column(Text, default="")
    budget_limit_usd: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32), default=PROJECT_STATUS_ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
