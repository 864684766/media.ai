"""Neo4j 连通性探测。"""

from neo4j import Driver

from app.storage.health_models import StorageHealthResult
from app.storage.neo4j import neo4j_constants as nc
from app.storage.neo4j.neo4j_driver_factory import create_neo4j_driver
from app.storage.neo4j.neo4j_settings_reader import is_neo4j_configured


def check_neo4j_health(driver: Driver | None = None) -> StorageHealthResult:
    """探测 Neo4j 是否可用。

    参数:
        driver: 可选外部 Driver，便于测试 mock。

    返回:
        StorageHealthResult: 统一健康检查结果。
    """
    if not is_neo4j_configured():
        return _not_configured_result()
    return _probe_driver(driver)


def _not_configured_result() -> StorageHealthResult:
    """未配置 Neo4j 时的结果。"""
    return StorageHealthResult(
        backend="neo4j",
        configured=False,
        reachable=False,
        message="未配置 NEO4J_URI/NEO4J_PASSWORD，跳过连接（Phase 2 前可暂不填）",
    )


def _probe_driver(driver: Driver | None) -> StorageHealthResult:
    """对已配置的 Neo4j 执行 RETURN 1。"""
    active_driver = driver if driver is not None else create_neo4j_driver()
    if active_driver is None:
        return _missing_auth_result()
    return _run_health_cypher(active_driver)


def _missing_auth_result() -> StorageHealthResult:
    """URI 有但密码缺失。"""
    return StorageHealthResult(
        backend="neo4j",
        configured=True,
        reachable=False,
        message="已配置 NEO4J_URI 但缺少 NEO4J_PASSWORD",
    )


def _run_health_cypher(driver: Driver) -> StorageHealthResult:
    """执行健康 Cypher。"""
    try:
        with driver.session() as session:
            session.run(nc.NEO4J_HEALTH_CYPHER).consume()
        return StorageHealthResult(
            backend="neo4j",
            configured=True,
            reachable=True,
            message="Neo4j 连接正常",
        )
    except Exception as exc:  # noqa: BLE001
        return StorageHealthResult(
            backend="neo4j",
            configured=True,
            reachable=False,
            message=f"Neo4j 连接失败：{exc}",
        )
