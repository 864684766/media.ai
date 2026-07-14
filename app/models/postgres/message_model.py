"""Message ORM 模型。

【职责】
    映射 PostgreSQL messages 表，保存每一轮 user / assistant 消息。

【与 LangGraph 的关系】
    load_history 读取本表；save_messages 写入本表。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class MessageModel(Base):
    """消息表 ORM。

    字段说明:
        id: 自增主键。
        conversation_id: 所属会话 id。
        role: 消息角色，user / assistant / system。
        content: 消息正文。
        created_at: 创建时间。
    """

    __tablename__ = pc.TABLE_MESSAGES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey(pc.CONVERSATION_FK))
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    conversation = relationship("ConversationModel", back_populates="messages")
