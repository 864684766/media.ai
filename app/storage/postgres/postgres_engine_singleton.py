"""PostgreSQL Engine 单例工厂。

每次 API 请求若新建 Engine 会耗尽远程 PG 连接数；全局复用同一连接池。
"""

from threading import Lock

from sqlalchemy import Engine

from app.storage.postgres.postgres_engine_builder import build_postgres_engine as _build_engine
from app.storage.postgres.postgres_settings_reader import get_postgres_url

_engine: Engine | None = None
_engine_lock = Lock()


def get_shared_postgres_engine() -> Engine | None:
    """返回进程内共享 Engine；未配置 DATABASE_URL 时 None。"""
    global _engine
    url = get_postgres_url()
    if url is None:
        return None
    if _engine is not None:
        return _engine
    with _engine_lock:
        if _engine is None:
            _engine = _build_engine(url)
        return _engine
