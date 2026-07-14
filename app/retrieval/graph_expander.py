"""Neo4j 图谱扩展（GraphRAG 轻量实现）。

【职责】
    按实体名在 Chunk 文本中做 CONTAINS 扩展，补充 Hybrid 召回。
"""

import logging
from typing import Any

from neo4j import Driver

from app.retrieval.retrieval_models import RetrievedChunk
from app.storage.neo4j import neo4j_constants as nc
from app.storage.neo4j.neo4j_driver_factory import create_neo4j_driver
from app.storage.neo4j.neo4j_query_runner import run_read_cypher

logger = logging.getLogger(__name__)

EXPAND_BY_ENTITY_CYPHER = (
    f"MATCH (c:{nc.LABEL_CHUNK}) "
    "WHERE $project_id IS NULL OR c.project_id = $project_id "
    "AND any(e IN $entities WHERE c.text CONTAINS e) "
    f"RETURN c.id AS {nc.KNN_COLUMN_CHUNK_ID}, c.text AS {nc.KNN_COLUMN_TEXT}, "
    f"c.source AS {nc.KNN_COLUMN_SOURCE}, 0.5 AS {nc.KNN_COLUMN_SCORE} "
    f"LIMIT $limit"
)


def expand_chunks_by_entities(
    entities: list[str],
    project_id: str | None,
    limit: int,
    driver: Driver | None = None,
) -> list[RetrievedChunk]:
    """按实体扩展 chunk 证据。"""
    if not entities:
        return []
    active_driver = driver if driver is not None else create_neo4j_driver()
    if active_driver is None:
        return []
    rows = _query_entities(active_driver, entities, project_id, limit)
    return [_row_to_chunk(row) for row in rows if _row_to_chunk(row) is not None]


def _query_entities(
    driver: Driver,
    entities: list[str],
    project_id: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    """执行图谱扩展查询。"""
    params = {"entities": entities, "project_id": project_id, "limit": limit}
    try:
        return run_read_cypher(EXPAND_BY_ENTITY_CYPHER, driver=driver, parameters=params)
    except Exception as exc:  # noqa: BLE001
        logger.warning("GraphRAG 扩展失败: %s", exc)
        return []


def _row_to_chunk(row: dict[str, Any]) -> RetrievedChunk | None:
    """Neo4j 行转 RetrievedChunk；无文本时跳过。"""
    text = str(row.get(nc.KNN_COLUMN_TEXT, "")).strip()
    if not text:
        return None
    return RetrievedChunk(
        chunk_id=str(row.get(nc.KNN_COLUMN_CHUNK_ID, "")),
        text=text,
        score=float(row.get(nc.KNN_COLUMN_SCORE, 0.0)),
        source=str(row.get(nc.KNN_COLUMN_SOURCE, "")),
    )
