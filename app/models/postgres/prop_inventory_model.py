"""道具清单 ORM 模型。

【职责】
    映射 prop_inventory 表，跨镜道具一致性资产（V2）。
"""

from datetime import datetime

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class PropInventoryModel(Base):
    """道具清单表 ORM。

    主键:
        project_id + prop_id 联合唯一。
    """

    __tablename__ = pc.TABLE_PROP_INVENTORY

    project_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    prop_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    ref_image_urls: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
