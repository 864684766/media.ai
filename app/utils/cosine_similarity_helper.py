"""向量余弦相似度辅助（检索与路由共用）。"""

import math


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """计算两向量余弦相似度。"""
    if len(left) != len(right) or not left:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    norm_left = math.sqrt(sum(a * a for a in left))
    norm_right = math.sqrt(sum(b * b for b in right))
    if norm_left == 0.0 or norm_right == 0.0:
        return 0.0
    return dot / (norm_left * norm_right)
