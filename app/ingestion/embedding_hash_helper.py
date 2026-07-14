"""HashingEmbedder 的数学辅助函数。

【职责】
    为 app/ingestion/embedder.py 提供：文本 → 特征词 → 哈希桶计数 → L2 归一化。

【原理（初学者向）】
    真正的 embedding 由神经网络产生；本项目学习阶段用「哈希技巧（hashing trick）」
    模拟：把文本的二字组（bigram）通过稳定哈希映射到固定长度的向量桶上计数，
    再做 L2 归一化。相同文本必得相同向量；含相同词的文本向量更相近。
    优点：零依赖、确定性、可测试；缺点：语义能力远弱于真模型，生产应换 API embedder。
"""

import hashlib
import math

# bigram 大小：连续两个字符作为一个特征
NGRAM_SIZE = 2


def extract_features(text: str) -> list[str]:
    """把文本切成 bigram 特征列表。

    参数:
        text: 输入文本（去空白后处理）。

    返回:
        list[str]: bigram 列表；文本过短时退化为单字符列表。
    """
    compact = "".join(text.split())
    if len(compact) < NGRAM_SIZE:
        return list(compact)
    return [compact[i : i + NGRAM_SIZE] for i in range(len(compact) - 1)]


def stable_bucket(feature: str, dimension: int) -> int:
    """把特征稳定映射到 [0, dimension) 的桶下标。

    参数:
        feature: 单个特征词。
        dimension: 向量维度（桶数）。

    返回:
        int: 桶下标；跨进程/跨平台稳定（md5，而非内置 hash）。
    """
    digest = hashlib.md5(feature.encode("utf-8")).hexdigest()
    return int(digest, 16) % dimension


def l2_normalize(vector: list[float]) -> list[float]:
    """L2 归一化（使向量适合 cosine 相似度）。

    参数:
        vector: 原始计数向量。

    返回:
        list[float]: 归一化后的向量；全零向量原样返回。
    """
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return vector
    return [value / norm for value in vector]
