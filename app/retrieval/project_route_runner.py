"""作品库检索子链编排（Hybrid → Grader → Rewrite 回环 → Rerank）。

【职责】
    实现 sec-07 检索链内的 rewrite 回环与 GraphRAG 扩展入口。
"""

from app.core.runtime_config import RuntimeConfig
from app.retrieval.retrieval_protocols import ChunkGrader
from app.retrieval.graph_rag_helper import maybe_expand_chunks
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.query_rewriter import PassthroughRewriter, QueryRewriter
from app.retrieval.retrieval_protocols import ChunkReranker
from app.retrieval.retrieval_constants import VERDICT_IRRELEVANT, VERDICT_RELEVANT
from app.retrieval.retrieval_models import RetrievedChunk
from app.schemas.agent_state import RouteDecision


def run_project_route(
    retriever: HybridRetriever,
    question: str,
    route: RouteDecision,
    project_id: str | None,
    runtime_config: RuntimeConfig,
    grader: ChunkGrader,
    reranker: ChunkReranker,
    rewriter: QueryRewriter | PassthroughRewriter,
) -> tuple[list[RetrievedChunk], bool]:
    """执行作品库检索链。

    返回:
        tuple: (精排证据, 是否需 Web 兜底)。
    """
    query = _initial_query(question, route)
    retry = 0
    while retry <= runtime_config.max_retries:
        candidates = retriever.retrieve(query, project_id, runtime_config.retrieve_top_k)
        candidates = maybe_expand_chunks(question, candidates, runtime_config, project_id)
        grade = grader.grade(question, candidates)
        if grade.verdict == VERDICT_RELEVANT:
            ranked = reranker.rerank(question, candidates, runtime_config.rerank_top_k)
            return ranked, False
        if grade.verdict == VERDICT_IRRELEVANT and retry < runtime_config.max_retries:
            query = rewriter.rewrite(question, query)
            retry += 1
            continue
        return [], True
    return [], True


def _initial_query(question: str, route: RouteDecision) -> str:
    """取首个子查询或原问题。"""
    if route.sub_queries:
        return route.sub_queries[0]
    return question
