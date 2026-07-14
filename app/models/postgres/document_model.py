"""Document ORM 模型。

【职责】
    映射 PostgreSQL documents 表，保存原始导入文档（真相源）。
    对应 docs/ARCHITECTURE.html sec-04.2 的 documents 表草案。

【与 Ingestion 的关系】
    Ingestion 写库时先落 documents，再落 chunks；
    Neo4j 中的 :Document 节点由本表派生，可随时重建。
"""

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class DocumentModel(Base):
    """文档表 ORM。

    字段说明:
        id: 文档 id，字符串（如 novel-demo-chapter-1）。
        project_id: 所属项目 id，检索时按此过滤。
        source: 来源说明，如文件路径或章节名。
        text: 文档原文（真相源，Neo4j 数据可由此重建）。
        created_at: 创建时间。
    """

    __tablename__ = pc.TABLE_DOCUMENTS

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(255), default="")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    chunks = relationship("ChunkModel", back_populates="document")
