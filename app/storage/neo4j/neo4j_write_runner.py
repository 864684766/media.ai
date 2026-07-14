"""Neo4j 写事务执行器。

【职责】
    执行写入型 Cypher（MERGE / CREATE / 建索引），
    与只读执行器（neo4j_query_runner.py）对称。

【何时被调用】
    - app/storage/neo4j/neo4j_chunk_writer.py 写 Document/Chunk 节点
    - app/storage/neo4j/neo4j_vector_index.py 创建向量索引

【简例】
    run_write_cypher("MERGE (:Chunk {id: $id})", {"id": "doc:0"}, driver)
"""

from typing import Any

from neo4j import Driver

from app.storage.neo4j.neo4j_driver_factory import create_neo4j_driver
from app.storage.neo4j.neo4j_session_scope import neo4j_session_scope


def run_write_cypher(
    cypher: str,
    parameters: dict[str, Any] | None = None,
    driver: Driver | None = None,
) -> list[dict[str, Any]]:
    """执行写入 Cypher 并返回记录字典列表。

    参数:
        cypher: Cypher 语句。
        parameters: 绑定参数字典。
        driver: 可选外部 Driver；None 时按 .env 创建。

    返回:
        list[dict[str, Any]]: 每行一个 dict（写语句通常为空列表）。

    异常:
        RuntimeError: Neo4j 未配置时抛出。
    """
    params = parameters if parameters is not None else {}
    active_driver = driver if driver is not None else create_neo4j_driver()
    if active_driver is None:
        raise RuntimeError("Neo4j 未配置，无法执行写入 Cypher")
    with neo4j_session_scope(active_driver) as session:
        result = session.run(cypher, params)
        return [record.data() for record in result]
