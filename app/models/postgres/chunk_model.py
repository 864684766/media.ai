"""Chunk ORM 模型。

【职责】
    映射 PostgreSQL chunks 表，保存切分后的文本块（chunk_id 真相源）。
    对应 docs/ARCHITECTURE.html sec-04.7「Chunk ID 对齐」：
    PG 与 Neo4j 使用同一 chunk_id，是 Hybrid RRF 融合与 citation 回指的前提。

【与检索的关系】
    关键词路（app/storage/postgres/chunk_keyword_searcher.py）查本表；
    向量路查 Neo4j :Chunk 节点；两路按 chunk_id 去重融合。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.postgres.base import Base
from app.models.postgres.time_helper import utc_now
from app.storage.postgres import postgres_constants as pc


class ChunkModel(Base):
    """chunk 表 ORM。

    字段说明:
        chunk_id: chunk 唯一 id，格式 {document_id}:{index}，与 Neo4j :Chunk.id 相同。
        document_id: 所属文档 id（外键 documents.id）。
        project_id: 所属项目 id，检索过滤用。
        chunk_index: 文档内 chunk 序号（0 起）。
        text: chunk 文本。
        source: 来源说明（citation 展示用）。
        created_at: 创建时间。
    """

    __tablename__ = pc.TABLE_CHUNKS

    chunk_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey(pc.DOCUMENT_FK))
    project_id: Mapped[str] = mapped_column(String(64), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    document = relationship("DocumentModel", back_populates="chunks")
