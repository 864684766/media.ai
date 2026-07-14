"""Embedding API 常量。

【职责】
    集中维护各厂商 embedding 端点、模型名与协议键名。
"""

# 智谱 OpenAI 兼容 embedding 路径
ZHIPU_EMBEDDINGS_PATH = "/embeddings"
ZHIPU_EMBEDDING_MODEL = "embedding-2"

# OpenAI 兼容 embedding 请求/响应键名
EMBEDDING_FIELD_MODEL = "model"
EMBEDDING_FIELD_INPUT = "input"
EMBEDDING_FIELD_DATA = "data"
EMBEDDING_FIELD_EMBEDDING = "embedding"

# 智谱 embedding-2 默认维度
ZHIPU_EMBEDDING_DIMENSION = 1024
