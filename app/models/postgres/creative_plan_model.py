"""创作大纲 ORM（creative_plans 表）。"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.creative_plan_constants import PLAN_STATUS_AWAITING_REVIEW
from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class CreativePlanModel(Base):
    """创作大纲实体表。"""

    __tablename__ = pc.TABLE_CREATIVE_PLANS

    plan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(64), index=True)
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    creation_type: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(32), default=PLAN_STATUS_AWAITING_REVIEW)
    version: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(256), default="")
    content_json: Mapped[str] = mapped_column(Text, default="{}")
    content_md: Mapped[str] = mapped_column(Text, default="")
    user_feedback: Mapped[str] = mapped_column(Text, default="")
    clarification_session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    revision_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
