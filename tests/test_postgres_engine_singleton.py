"""postgres_engine_singleton 单元测试。"""

from app.storage.postgres.postgres_engine_factory import create_postgres_engine
from app.storage.postgres.postgres_engine_singleton import get_shared_postgres_engine


def test_create_postgres_engine_returns_same_instance(monkeypatch) -> None:
    """多次调用应返回同一 Engine 实例。"""
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:pass@127.0.0.1:5432/testdb",
    )
    import app.storage.postgres.postgres_engine_singleton as singleton_mod

    singleton_mod._engine = None
    first = create_postgres_engine()
    second = get_shared_postgres_engine()
    assert first is not None
    assert first is second
