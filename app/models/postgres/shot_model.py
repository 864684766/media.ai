"""Shot ORM 模型。

【职责】
    映射 PostgreSQL shots 表，保存结构化分镜（V1 真相源）。

【与 chat 的关系】
    chat + storyboard Skill 产出 JSON 文本；本表通过 video API / CLI 持久化。
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class ShotModel(Base):
    """分镜表 ORM。

    字段说明:
        shot_id: 主键，全局唯一。
        project_id: 业务项目 id（与 ChatRequest.project_id 一致）。
        shot_no: 镜号，用于排序与展示。
        duration_sec: 单镜时长（秒）。
        status: 镜头状态机当前值（V1 默认 draft）。
    """

    __tablename__ = pc.TABLE_SHOTS

    shot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), index=True)
    shot_no: Mapped[str] = mapped_column(String(32))
    duration_sec: Mapped[float] = mapped_column(Float)
    shot_size: Mapped[str] = mapped_column(String(64), default="")
    camera: Mapped[str] = mapped_column(String(128), default="")
    action: Mapped[str] = mapped_column(Text, default="")
    dialogue: Mapped[str] = mapped_column(Text, default="")
    sfx: Mapped[str] = mapped_column(String(128), default="")
    character_ids: Mapped[list] = mapped_column(JSON, default=list)
    scene_id: Mapped[str] = mapped_column(String(64), default="")
    prop_ids: Mapped[list] = mapped_column(JSON, default=list)
    keyframe_uri: Mapped[str] = mapped_column(String(512), default="")
    transition: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="")
    qa_attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
