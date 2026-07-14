"""PostgreSQL ORM 基类。

【职责】
    为所有 PG 表模型提供统一 DeclarativeBase。

【何时调用】
    SQLAlchemy 创建表、Repository 查询时会引用这里的 Base.metadata。

【示例】
    Base.metadata.create_all(engine) → 创建 conversations / messages 表（测试用）
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 PostgreSQL ORM Model 的共同基类。"""
