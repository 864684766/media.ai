"""PostgreSQL 元数据工具。

【职责】
    暴露 create_all_tables，供测试或本地学习快速创建表。

【注意】
    生产/协作环境请优先使用 Alembic：`poetry run alembic upgrade head`。
"""

from sqlalchemy.engine import Engine

from app.models.postgres import Base
from app.storage.postgres.orm_model_registry import register_all_orm_models


def create_all_tables(engine: Engine) -> None:
    """根据 ORM 模型创建全部表（测试/学习用）。

    参数:
        engine: SQLAlchemy Engine。
    """
    register_all_orm_models()
    Base.metadata.create_all(bind=engine)
