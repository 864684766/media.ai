"""Ingestion Lite 常量。

【职责】
    集中维护 ingestion 配置键、默认值和 chunk id 拼接规则。
"""

# app.yaml ingestion 段键名
YAML_KEY_INGESTION_SECTION = "ingestion"
YAML_KEY_CHUNK_SIZE = "chunk_size"
YAML_KEY_CHUNK_OVERLAP = "chunk_overlap"
YAML_KEY_DRY_RUN_DEFAULT = "dry_run_default"

# app.yaml ingestion.embedding 子段键名
YAML_KEY_EMBEDDING_SECTION = "embedding"
YAML_KEY_EMBEDDING_PROVIDER = "provider"
YAML_KEY_EMBEDDING_DIMENSION = "dimension"

# 默认切分参数
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 80
DEFAULT_DRY_RUN = True

# 默认 embedding 配置：hashing 为本地确定性向量（无需外部 API，学习/测试友好）
DEFAULT_EMBEDDING_PROVIDER = "hashing"
DEFAULT_EMBEDDING_DIMENSION = 256

# embedding provider 可选值
EMBEDDING_PROVIDER_HASHING = "hashing"
EMBEDDING_PROVIDER_ZHIPU = "zhipu"

# chunk id 形态：{document_id}:{index}
CHUNK_ID_SEPARATOR = ":"
