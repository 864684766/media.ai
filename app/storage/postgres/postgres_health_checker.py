"""PostgreSQL 连通性探测。

执行 SELECT 1，返回 StorageHealthResult；未配置时不连网。
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.storage.health_models import StorageHealthResult
from app.storage.postgres import postgres_constants as pc
from app.storage.postgres.postgres_engine_factory import create_postgres_engine
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


def check_postgres_health(engine: Engine | None = None) -> StorageHealthResult:
    """探测 PostgreSQL 是否可用。

    参数:
        engine: 可选外部 Engine，便于测试注入（注入时跳过 .env 是否配置检查）。

    返回:
        StorageHealthResult: 统一健康检查结果。
    """
    if engine is not None:
        return _run_health_sql(engine, configured=True)
    if not is_postgres_configured():
        return _not_configured_result()
    return _probe_engine(None)


def _not_configured_result() -> StorageHealthResult:
    """未配置 DATABASE_URL 时的结果。"""
    return StorageHealthResult(
        backend="postgres",
        configured=False,
        reachable=False,
        message="未配置 DATABASE_URL，跳过连接（本地开发可暂不填）",
    )


def _probe_engine(engine: Engine | None) -> StorageHealthResult:
    """对已配置的 PG 执行 SELECT 1。"""
    active_engine = engine if engine is not None else create_postgres_engine()
    if active_engine is None:
        return _not_configured_result()
    return _run_health_sql(active_engine, configured=True)


def _run_health_sql(engine: Engine, configured: bool) -> StorageHealthResult:
    """执行探测 SQL 并封装结果。"""
    try:
        with engine.connect() as conn:
            conn.execute(text(pc.PG_HEALTH_SQL))
        return StorageHealthResult(
            backend="postgres",
            configured=configured,
            reachable=True,
            message="PostgreSQL 连接正常",
        )
    except Exception as exc:  # noqa: BLE001 — 健康检查需捕获所有连接错误
        return StorageHealthResult(
            backend="postgres",
            configured=configured,
            reachable=False,
            message=f"PostgreSQL 连接失败：{exc}",
        )
