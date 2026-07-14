"""Conversation ORM 模型。

【职责】
    映射 PostgreSQL conversations 表，保存一次多轮会话的根记录。

【与 LangGraph 的关系】
    conversation_id 会作为业务会话 id；后续 thread_id 默认等于 conversation_id。
"""

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class ConversationModel(Base):
    """会话表 ORM。

    字段说明:
        id: 会话 id，字符串 UUID。
        project_id: 可选项目 id，用于隔离小说/视频项目。
        creation_type: 创作类型 novel | video，创建后不可混用。
        summary: 历史压缩摘要，后续 compact_history 写入。
        created_at: 创建时间。
        updated_at: 更新时间。
    """

    __tablename__ = pc.TABLE_CONVERSATIONS

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    creation_type: Mapped[str | None] = mapped_column(String(16), nullable=True, default=None)
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    messages = relationship("MessageModel", back_populates="conversation")
