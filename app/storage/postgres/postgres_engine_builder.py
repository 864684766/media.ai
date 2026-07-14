"""Engine 构建（连接池参数）。"""

from sqlalchemy import Engine, create_engine

from app.storage.postgres import postgres_constants as pc


def build_postgres_engine(url: str) -> Engine:
    """使用项目默认连接池参数构建 Engine。"""
    return create_engine(
        url,
        pool_size=pc.PG_POOL_SIZE,
        max_overflow=pc.PG_MAX_OVERFLOW,
        pool_pre_ping=pc.PG_POOL_PRE_PING,
        pool_recycle=pc.PG_POOL_RECYCLE_SEC,
    )
