"""Neo4j Chunk 写入 Cypher 语句模板。

【职责】
    集中存放 Chunk 写入相关的 Cypher 文本，
    写入器（neo4j_chunk_writer.py）只负责组织参数与调用。

【设计要点】
    - 全部用 MERGE 保证幂等：重复导入同一文档不会产生重复节点
    - chunk 的 id 与 PG chunks.chunk_id 完全一致（sec-04.7 Chunk ID 对齐）
"""

from app.storage.neo4j import neo4j_constants as nc

# 写入 Document 节点（幂等）
MERGE_DOCUMENT_CYPHER = (
    f"MERGE (d:{nc.LABEL_DOCUMENT} {{id: $document_id}}) "
    "SET d.project_id = $project_id, d.source = $source"
)

# 写入 Chunk 节点并挂到 Document 下（幂等）
MERGE_CHUNK_CYPHER = (
    f"MATCH (d:{nc.LABEL_DOCUMENT} {{id: $document_id}}) "
    f"MERGE (c:{nc.LABEL_CHUNK} {{id: $chunk_id}}) "
    "SET c.text = $text, c.embedding = $embedding, "
    "c.chunk_index = $chunk_index, c.project_id = $project_id, c.source = $source "
    f"MERGE (d)-[:{nc.REL_HAS_CHUNK}]->(c)"
)

# 相邻 chunk 建 NEXT 边（幂等），供检索时向前后扩展上下文
MERGE_NEXT_EDGE_CYPHER = (
    f"MATCH (a:{nc.LABEL_CHUNK} {{id: $from_chunk_id}}) "
    f"MATCH (b:{nc.LABEL_CHUNK} {{id: $to_chunk_id}}) "
    f"MERGE (a)-[:{nc.REL_NEXT}]->(b)"
)
