"""Rerank 对外入口（兼容旧 import 路径）。"""

from app.retrieval.rerank_factory import build_reranker
from app.retrieval.retrieval_protocols import ChunkReranker
from app.retrieval.retrieval_models import RetrievedChunk

_default_reranker: ChunkReranker | None = None


def rerank_chunks(
    question: str,
    chunks: list[RetrievedChunk],
    top_k: int,
    reranker: ChunkReranker | None = None,
) -> list[RetrievedChunk]:
    """精排并截断证据列表。"""
    active = reranker if reranker is not None else _get_default_reranker()
    return active.rerank(question, chunks, top_k)


def _get_default_reranker() -> ChunkReranker:
    """懒加载默认 Reranker。"""
    global _default_reranker
    if _default_reranker is None:
        _default_reranker = build_reranker()
    return _default_reranker
