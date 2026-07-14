"""PostgreSQL Session 作用域。

提供 with 块内使用的 Session，结束自动 close。
"""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.storage.postgres.postgres_engine_factory import create_postgres_engine


@contextmanager
def postgres_session_scope(engine: Engine | None = None) -> Iterator[Session]:
    """在 with 块内提供 SQLAlchemy Session。

    参数:
        engine: 可选外部 Engine；为 None 时内部 create_postgres_engine()。

     yields:
        Session: 数据库会话。

    异常:
        RuntimeError: 未配置 DATABASE_URL 时抛出。
    """
    active_engine = engine if engine is not None else create_postgres_engine()
    if active_engine is None:
        raise RuntimeError("PostgreSQL 未配置：请在 .env 设置 DATABASE_URL")
    session = _open_session(active_engine)
    try:
        yield session
    finally:
        session.close()


def _open_session(engine: Engine) -> Session:
    """为指定 Engine 创建 Session。"""
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return factory()
