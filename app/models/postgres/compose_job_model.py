"""合成 Job ORM（V5）。"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class ComposeJobModel(Base):
    """compose_jobs 表。"""

    __tablename__ = pc.TABLE_COMPOSE_JOBS

    job_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32))
    total_shots: Mapped[int] = mapped_column(Integer, default=0)
    output_uri: Mapped[str] = mapped_column(String(512), default="")
    timeline_json: Mapped[str] = mapped_column(Text, default="")
    subtitle_uri: Mapped[str] = mapped_column(String(512), default="")
    audio_tracks_json: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
