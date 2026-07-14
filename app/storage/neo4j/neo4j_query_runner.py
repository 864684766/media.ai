"""Neo4j 只读 Cypher 执行器（骨架）。

Phase 2 检索链会在此扩展 vector / 图遍历查询。
"""

from typing import Any

from neo4j import Driver, Session

from app.storage.neo4j.neo4j_driver_factory import create_neo4j_driver
from app.storage.neo4j.neo4j_session_scope import neo4j_session_scope


def run_read_cypher(
    cypher: str,
    parameters: dict[str, Any] | None = None,
    driver: Driver | None = None,
) -> list[dict[str, Any]]:
    """执行只读 Cypher 并返回记录字典列表。

    参数:
        cypher: Cypher 语句。
        parameters: 绑定参数字典。
        driver: 可选外部 Driver。

    返回:
        list[dict[str, Any]]: 每行一个 dict。
    """
    params = parameters if parameters is not None else {}
    active_driver = driver if driver is not None else create_neo4j_driver()
    if active_driver is None:
        raise RuntimeError("Neo4j 未配置，无法执行 Cypher")
    return _execute_read(active_driver, cypher, params)


def _execute_read(
    driver: Driver,
    cypher: str,
    parameters: dict[str, Any],
) -> list[dict[str, Any]]:
    """在 Session 内执行 read 事务。"""
    with neo4j_session_scope(driver) as session:
        return _collect_records(session, cypher, parameters)


def _collect_records(
    session: Session,
    cypher: str,
    parameters: dict[str, Any],
) -> list[dict[str, Any]]:
    """收集 Result 为 dict 列表。"""
    result = session.run(cypher, parameters)
    return [record.data() for record in result]
