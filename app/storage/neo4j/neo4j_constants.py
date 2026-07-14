"""Neo4j 存储层常量。

【职责】
    集中管理标签名、边类型、向量索引名等 Cypher 字面量，
    写入器与检索器统一引用，改名只改一处。
"""

# 健康检查 Cypher
NEO4J_HEALTH_CYPHER = "RETURN 1 AS ok"

# Driver 默认配置
NEO4J_DRIVER_MAX_CONNECTION_LIFETIME = 3600
NEO4J_MAX_CONNECTION_POOL_SIZE = 10

# 节点标签（与 docs/ARCHITECTURE.html sec-04.3 图谱模型一致）
LABEL_DOCUMENT = "Document"
LABEL_CHUNK = "Chunk"

# 边类型
REL_HAS_CHUNK = "HAS_CHUNK"
REL_NEXT = "NEXT"

# 向量索引名（chunk embedding 近邻查询用）
CHUNK_VECTOR_INDEX_NAME = "chunk_embedding_index"

# 向量相似度函数（cosine 适合归一化后的文本向量）
VECTOR_SIMILARITY_FUNCTION = "cosine"

# kNN 查询返回列名（Cypher RETURN ... AS 别名与消费方 row.get 共用，一处权威）
KNN_COLUMN_CHUNK_ID = "chunk_id"
KNN_COLUMN_TEXT = "text"
KNN_COLUMN_SOURCE = "source"
KNN_COLUMN_CHUNK_INDEX = "chunk_index"
KNN_COLUMN_SCORE = "score"
