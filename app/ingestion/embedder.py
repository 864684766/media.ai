"""文本 Embedder（向量化器）。

【职责】
    把文本转成固定维度的向量，供 Neo4j 向量索引与检索的向量路使用。
    对应 docs/ARCHITECTURE.html sec-13「切分 → embedding → 写 PG + Neo4j」。

【当前实现】
    HashingEmbedder：本地确定性向量（哈希技巧），零外部依赖，学习/测试友好。
    原理见 app/ingestion/embedding_hash_helper.py 顶部说明。

【如何换成真模型】
    实现同样带 dimension 属性与 embed_texts() 方法的类
    （如调用智谱 embedding API），在 embedder_factory.build_embedder() 注册即可，
    调用方（database_feed_adapter / retrieval）不需要改。
"""

from typing import Protocol

from app.ingestion import ingestion_constants as ic
from app.ingestion.embedding_hash_helper import (
    extract_features,
    l2_normalize,
    stable_bucket,
)

__all__ = ["Embedder", "HashingEmbedder"]


class Embedder(Protocol):
    """Embedder 统一接口。

    属性说明:
        dimension: 输出向量维度（必须与 Neo4j 向量索引维度一致）。
    """

    dimension: int

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """把一批文本转成向量。

        参数:
            texts: 文本列表。

        返回:
            list[list[float]]: 与输入一一对应的向量列表。
        """
        ...


class HashingEmbedder:
    """哈希技巧 Embedder（本地确定性，学习用）。

    参数说明:
        dimension: 向量维度；默认取 ingestion_constants.DEFAULT_EMBEDDING_DIMENSION。
    """

    def __init__(self, dimension: int = ic.DEFAULT_EMBEDDING_DIMENSION) -> None:
        """初始化并记录维度。"""
        self.dimension = dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量向量化。

        参数:
            texts: 文本列表。

        返回:
            list[list[float]]: L2 归一化后的向量列表。
        """
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        """向量化单条文本：bigram 特征 → 哈希桶计数 → 归一化。"""
        vector = [0.0] * self.dimension
        for feature in extract_features(text):
            vector[stable_bucket(feature, self.dimension)] += 1.0
        return l2_normalize(vector)
