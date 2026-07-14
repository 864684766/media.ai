"""Grader 对外入口（兼容旧 import 路径）。"""

from app.retrieval.grader_factory import build_grader
from app.retrieval.retrieval_protocols import ChunkGrader
from app.retrieval.retrieval_models import GradeResult, RetrievedChunk

_default_grader: ChunkGrader | None = None


def grade_chunks(
    question: str,
    chunks: list[RetrievedChunk],
    grader: ChunkGrader | None = None,
) -> GradeResult:
    """评估证据相关性。

    参数:
        question: 用户问题。
        chunks: Hybrid 检索结果。
        grader: 可选注入的 Grader；None 时用工厂默认实例。

    返回:
        GradeResult: 判定结果。
    """
    active = grader if grader is not None else _get_default_grader()
    return active.grade(question, chunks)


def _get_default_grader() -> ChunkGrader:
    """懒加载默认 Grader。"""
    global _default_grader
    if _default_grader is None:
        _default_grader = build_grader()
    return _default_grader
