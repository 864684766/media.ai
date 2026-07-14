"""音频资产 ORM（V8 audio_assets 表）。"""

from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.audio_constants import AUDIO_SOURCE_TTS, TRACK_TYPE_DIALOGUE
from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class AudioAssetModel(Base):
    """对白/BGM/音效轨登记。"""

    __tablename__ = pc.TABLE_AUDIO_ASSETS

    audio_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), index=True)
    shot_id: Mapped[str] = mapped_column(String(64), default="")
    track_type: Mapped[str] = mapped_column(String(32), default=TRACK_TYPE_DIALOGUE)
    uri: Mapped[str] = mapped_column(String(512), default="")
    duration_sec: Mapped[float] = mapped_column(Float, default=0.0)
    voice_id: Mapped[str] = mapped_column(String(64), default="")
    source: Mapped[str] = mapped_column(String(32), default=AUDIO_SOURCE_TTS)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
