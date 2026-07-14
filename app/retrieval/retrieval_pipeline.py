"""检索流水线编排器（含 Grader 回环与 GraphRAG）。

【职责】
    按 RouteDecision 执行 Hybrid → Grader → Rewrite → Rerank → Web 兜底链。
"""

from app.core.runtime_config import RuntimeConfig
from app.retrieval.grader_factory import build_grader
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.project_route_runner import run_project_route
from app.retrieval.query_rewriter import PassthroughRewriter, QueryRewriter, build_query_rewriter
from app.retrieval.rerank_factory import build_reranker
from app.retrieval.retrieval_protocols import ChunkGrader, ChunkReranker
from app.retrieval.retrieval_models import RetrievalContext, RetrievedChunk, WebResult
from app.retrieval.web_search import TavilyWebSearcher
from app.schemas.agent_state import RouteDecision


class RetrievalPipeline:
    """检索链编排。"""

    def __init__(
        self,
        retriever: HybridRetriever | None,
        web_searcher: TavilyWebSearcher | None,
        grader: ChunkGrader | None = None,
        reranker: ChunkReranker | None = None,
        rewriter: QueryRewriter | PassthroughRewriter | None = None,
    ) -> None:
        """登记依赖与可选 Grader/Rerank/Rewriter。"""
        self._retriever = retriever
        self._web_searcher = web_searcher
        self._grader = grader if grader is not None else build_grader()
        self._reranker = reranker if reranker is not None else build_reranker()
        self._rewriter = rewriter if rewriter is not None else build_query_rewriter()

    def run(
        self,
        question: str,
        route: RouteDecision,
        project_id: str | None,
        runtime_config: RuntimeConfig,
    ) -> RetrievalContext:
        """按能力开关执行检索链。"""
        chunks: list[RetrievedChunk] = []
        web_results: list[WebResult] = []
        need_web_fallback = False
        if route.needs_project and self._retriever is not None:
            chunks, need_web_fallback = run_project_route(
                self._retriever,
                question,
                route,
                project_id,
                runtime_config,
                self._grader,
                self._reranker,
                self._rewriter,
            )
        if route.needs_web or need_web_fallback:
            web_results = self._run_web_route(question)
        return RetrievalContext(chunks=chunks, web_results=web_results)

    def _run_web_route(self, question: str) -> list[WebResult]:
        """Web 路。"""
        if self._web_searcher is None:
            return []
        return self._web_searcher.search(question)
