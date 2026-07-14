"""澄清会话 ORM（clarification_sessions 表）。"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.clarification_constants import CLARIFICATION_STATUS_COLLECTING
from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class ClarificationSessionModel(Base):
    """创作澄清会话表。"""

    __tablename__ = pc.TABLE_CLARIFICATION_SESSIONS

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(64), index=True)
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    creation_type: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(32), default=CLARIFICATION_STATUS_COLLECTING)
    round: Mapped[int] = mapped_column(Integer, default=1)
    questions_json: Mapped[str] = mapped_column(Text, default="[]")
    answers_json: Mapped[str] = mapped_column(Text, default="[]")
    requirements_summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
