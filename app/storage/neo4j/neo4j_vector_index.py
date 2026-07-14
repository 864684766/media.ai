"""Neo4j 向量索引管理与近邻查询。

【职责】
    1. ensure_chunk_vector_index：创建 Chunk.embedding 上的向量索引（幂等）
    2. query_similar_chunks：用向量索引做 kNN 近邻查询（Hybrid 检索的向量路）

【对应设计】
    docs/ARCHITECTURE.html sec-04.5：向量相似不预存边，查询时经 vector index 计算。
    Neo4j 5.15+ 支持 CREATE VECTOR INDEX 语法。

【简例】
    ensure_chunk_vector_index(driver, dimension=256)
    rows = query_similar_chunks(driver, embedding, top_k=5, project_id="demo")
"""

from typing import Any

from neo4j import Driver

from app.storage.neo4j import neo4j_constants as nc
from app.storage.neo4j.neo4j_query_runner import run_read_cypher
from app.storage.neo4j.neo4j_write_runner import run_write_cypher

# 创建向量索引模板（IF NOT EXISTS 保证幂等）。
# 注意：Neo4j 的 schema 命令不支持 $ 参数绑定，dimension 只能内联为字面量，
# 由 build_create_vector_index_cypher() 在调用时填入。
CREATE_VECTOR_INDEX_TEMPLATE = (
    f"CREATE VECTOR INDEX {nc.CHUNK_VECTOR_INDEX_NAME} IF NOT EXISTS "
    f"FOR (c:{nc.LABEL_CHUNK}) ON (c.embedding) "
    "OPTIONS {{indexConfig: {{`vector.dimensions`: {dimension}, "
    f"`vector.similarity_function`: '{nc.VECTOR_SIMILARITY_FUNCTION}'"
    "}}}}"
)


def build_create_vector_index_cypher(dimension: int) -> str:
    """生成建向量索引的 Cypher（维度内联为字面量）。

    参数:
        dimension: 向量维度，必须为正整数。

    返回:
        str: 可直接执行的 Cypher 语句。

    异常:
        ValueError: 维度不是正整数时抛出（防止拼接非法语句）。
    """
    if dimension <= 0:
        raise ValueError(f"向量维度必须为正整数，收到: {dimension}")
    return CREATE_VECTOR_INDEX_TEMPLATE.format(dimension=int(dimension))

# kNN 近邻查询：db.index.vector.queryNodes 返回 (node, score)
# RETURN 别名取自 neo4j_constants，与消费方（hybrid_factory）共用同一套列名
QUERY_SIMILAR_CHUNKS_CYPHER = (
    "CALL db.index.vector.queryNodes($index_name, $top_k, $embedding) "
    "YIELD node, score "
    "WHERE $project_id IS NULL OR node.project_id = $project_id "
    f"RETURN node.id AS {nc.KNN_COLUMN_CHUNK_ID}, node.text AS {nc.KNN_COLUMN_TEXT}, "
    f"node.source AS {nc.KNN_COLUMN_SOURCE}, node.chunk_index AS {nc.KNN_COLUMN_CHUNK_INDEX}, "
    f"score AS {nc.KNN_COLUMN_SCORE} "
    f"ORDER BY {nc.KNN_COLUMN_SCORE} DESC"
)


def ensure_chunk_vector_index(driver: Driver, dimension: int) -> None:
    """创建 Chunk 向量索引（已存在则跳过）。

    参数:
        driver: Neo4j Driver。
        dimension: 向量维度，必须与 embedder 输出一致。
    """
    run_write_cypher(
        build_create_vector_index_cypher(dimension),
        driver=driver,
    )


def query_similar_chunks(
    driver: Driver,
    embedding: list[float],
    top_k: int,
    project_id: str | None = None,
) -> list[dict[str, Any]]:
    """向量近邻查询（Hybrid 检索的向量路）。

    参数:
        driver: Neo4j Driver。
        embedding: 查询向量（与索引维度一致）。
        top_k: 最多返回条数。
        project_id: 项目过滤；None 时不过滤。

    返回:
        list[dict]: 每行含 chunk_id / text / source / chunk_index / score。
    """
    return run_read_cypher(
        QUERY_SIMILAR_CHUNKS_CYPHER,
        {
            "index_name": nc.CHUNK_VECTOR_INDEX_NAME,
            "top_k": top_k,
            "embedding": embedding,
            "project_id": project_id,
        },
        driver=driver,
    )
