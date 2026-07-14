"""PostgreSQL Engine 工厂。

创建 SQLAlchemy Engine；无 DATABASE_URL 时不创建，返回 None。
进程内复用单例连接池（见 postgres_engine_singleton）。
"""

from sqlalchemy import Engine

from app.storage.postgres.postgres_engine_singleton import get_shared_postgres_engine


def create_postgres_engine() -> Engine | None:
    """根据 .env 返回共享 SQLAlchemy Engine。

    返回:
        Engine | None: 未配置 DATABASE_URL 时返回 None。
    """
    return get_shared_postgres_engine()
