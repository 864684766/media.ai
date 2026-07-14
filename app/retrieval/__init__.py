"""检索流水线模块（Hybrid RAG）。

【职责】
    实现 docs/ARCHITECTURE.html sec-06 / sec-07 的检索链：
    Hybrid（关键词 + 向量）→ RRF 融合 → Grader 评估 → Rerank 精排 → Web 兜底。

【与图的关系】
    app/graph/nodes/retrieve_hybrid.py 等薄节点调用本模块；
    本模块不感知 LangGraph，只做「问题 → 证据」的纯逻辑。
"""

from app.retrieval.retrieval_models import (
    GradeResult,
    RetrievalContext,
    RetrievedChunk,
    WebResult,
)

__all__ = [
    "GradeResult",
    "RetrievalContext",
    "RetrievedChunk",
    "WebResult",
]
