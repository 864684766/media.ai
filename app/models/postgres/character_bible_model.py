"""角色圣经 ORM 模型。

【职责】
    映射 character_bible 表，锁定角色外观与参考图（V2 一致性资产）。
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class CharacterBibleModel(Base):
    """角色圣经表 ORM。

    主键:
        project_id + character_id 联合唯一。
    """

    __tablename__ = pc.TABLE_CHARACTER_BIBLE

    project_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    character_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), default="")
    appearance: Mapped[str] = mapped_column(Text, default="")
    costume: Mapped[str] = mapped_column(Text, default="")
    age_band: Mapped[str] = mapped_column(String(32), default="")
    ref_image_urls: Mapped[list] = mapped_column(JSON, default=list)
    voice_id: Mapped[str] = mapped_column(String(64), default="")
    lock_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
