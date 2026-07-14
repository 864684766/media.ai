"""Neo4j Session 作用域。

提供 with 块内使用的 Session，结束自动 close 并归还 Driver 连接池。
"""

from collections.abc import Iterator
from contextlib import contextmanager

from neo4j import Driver, Session

from app.storage.neo4j.neo4j_driver_factory import create_neo4j_driver
from app.storage.neo4j.neo4j_driver_singleton import reset_shared_neo4j_driver


@contextmanager
def neo4j_session_scope(driver: Driver | None = None) -> Iterator[Session]:
    """在 with 块内提供 Neo4j Session。

    参数:
        driver: 可选外部 Driver；为 None 时使用进程内共享 Driver。

    yields:
        Session: Neo4j 会话。

    异常:
        RuntimeError: 未配置 Neo4j 时抛出。
    """
    active_driver = driver if driver is not None else create_neo4j_driver()
    if active_driver is None:
        raise RuntimeError("Neo4j 未配置：请在 .env 设置 NEO4J_URI 与 NEO4J_PASSWORD")
    session = active_driver.session()
    try:
        yield session
    finally:
        session.close()


def close_neo4j_driver(driver: Driver | None) -> None:
    """关闭 Driver 释放连接池（仅用于测试 teardown 或非共享实例）。

    参数:
        driver: 外部创建的 Driver；若为 None 则释放进程内共享 Driver。
    """
    if driver is None:
        reset_shared_neo4j_driver()
        return
    driver.close()
