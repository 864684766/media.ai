"""检索链协议类型（避免工厂与编排器循环 import）。"""

from typing import Protocol

from app.retrieval.retrieval_models import GradeResult, RetrievedChunk


class ChunkGrader(Protocol):
    """Grader 统一接口。"""

    def grade(self, question: str, chunks: list[RetrievedChunk]) -> GradeResult:
        """评估相关性。"""
        ...


class ChunkReranker(Protocol):
    """Rerank 统一接口。"""

    def rerank(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        """精排并截断。"""
        ...
