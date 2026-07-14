"""HashingEmbedder 测试。

【覆盖点】
    1. 输出维度正确且已 L2 归一化。
    2. 相同文本向量完全一致（确定性）。
    3. 相似文本的余弦相似度高于无关文本。
    4. build_embedder 对未知 provider 报错。
"""

import math

import pytest

from app.ingestion.embedder import HashingEmbedder
from app.ingestion.embedder_factory import build_embedder


def _cosine(a: list[float], b: list[float]) -> float:
    """计算余弦相似度（向量已归一化时即点积）。"""
    return sum(x * y for x, y in zip(a, b))


def test_embedding_dimension_and_norm() -> None:
    """向量长度应等于 dimension，且 L2 范数约等于 1。"""
    embedder = HashingEmbedder(dimension=64)
    [vector] = embedder.embed_texts(["张三拜青云子为师"])
    assert len(vector) == 64
    norm = math.sqrt(sum(value * value for value in vector))
    assert norm == pytest.approx(1.0)


def test_embedding_is_deterministic() -> None:
    """相同文本必须得到完全相同的向量。"""
    embedder = HashingEmbedder(dimension=64)
    first = embedder.embed_texts(["青云宗山门"])[0]
    second = embedder.embed_texts(["青云宗山门"])[0]
    assert first == second


def test_similar_text_scores_higher() -> None:
    """相似文本的余弦相似度应高于无关文本。"""
    embedder = HashingEmbedder(dimension=256)
    query, similar, unrelated = embedder.embed_texts(
        ["张三的师父是青云子", "青云子收张三为徒", "今天天气晴朗适合出游"]
    )
    assert _cosine(query, similar) > _cosine(query, unrelated)


def test_build_embedder_falls_back_for_unknown_provider() -> None:
    """未知 provider 应回退 hashing，不抛异常。"""
    embedder = build_embedder(provider="unknown-model")
    assert isinstance(embedder, HashingEmbedder)
