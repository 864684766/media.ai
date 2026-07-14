"""检索流水线单元测试（RRF / Hybrid / Grader / Rerank / Web）。

【覆盖点】
    1. RRF：两路都靠前的 chunk 融合分最高，按 chunk_id 去重。
    2. Hybrid：单路缺席时退化为单路检索。
    3. Grader：有重叠证据 relevant，无证据 no_evidence。
    4. Rerank：按重叠分截断 top_k。
    5. TavilyWebSearcher：无 Key 返回空；MockTransport 下解析结果。
"""

import httpx

from app.core.config_resolver import resolve
from app.retrieval.grader import grade_chunks
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.rerank import rerank_chunks
from app.retrieval.retrieval_constants import VERDICT_NO_EVIDENCE, VERDICT_RELEVANT
from app.retrieval.retrieval_models import RetrievedChunk
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.retrieval.rrf import fuse_ranked_lists
from app.retrieval.web_search import TavilyWebSearcher
from app.schemas.agent_state import RouteDecision


def _chunk(chunk_id: str, text: str, score: float = 1.0) -> RetrievedChunk:
    """构造测试 chunk。"""
    return RetrievedChunk(chunk_id=chunk_id, text=text, score=score)


def test_rrf_prefers_chunks_in_both_routes() -> None:
    """两路都出现的 chunk 应排到最前，且不重复。"""
    keyword = [_chunk("a", "文本A"), _chunk("b", "文本B")]
    vector = [_chunk("b", "文本B"), _chunk("c", "文本C")]
    fused = fuse_ranked_lists([keyword, vector])
    assert [chunk.chunk_id for chunk in fused][0] == "b"
    assert len(fused) == 3


def test_hybrid_degrades_to_single_route() -> None:
    """向量路缺席时应只用关键词路结果。"""
    keyword_route = lambda query, project_id, top_k: [_chunk("k1", "关键词结果")]  # noqa: E731
    retriever = HybridRetriever(keyword_route, vector_route=None)
    results = retriever.retrieve("问题", project_id=None, top_k=10)
    assert [chunk.chunk_id for chunk in results] == ["k1"]


def test_grader_verdicts() -> None:
    """有词重叠 → relevant；空候选 → no_evidence。"""
    chunks = [_chunk("a", "张三拜青云子为师")]
    assert grade_chunks("张三的师父", chunks).verdict == VERDICT_RELEVANT
    assert grade_chunks("张三的师父", []).verdict == VERDICT_NO_EVIDENCE


def test_rerank_truncates_to_top_k() -> None:
    """精排后应只保留 top_k 条，且相关的排前面。"""
    chunks = [
        _chunk("far", "无关内容", score=0.1),
        _chunk("hit", "张三的师父是青云子", score=0.1),
        _chunk("mid", "张三下山历练", score=0.1),
    ]
    result = rerank_chunks("张三的师父", chunks, top_k=2)
    assert len(result) == 2
    assert result[0].chunk_id == "hit"


def test_web_searcher_without_key_returns_empty() -> None:
    """未配置 API Key 时应静默返回空列表。"""
    searcher = TavilyWebSearcher(api_key=None)
    searcher._api_key = None  # 确保环境变量不干扰
    assert searcher.search("今天新闻") == []


def test_web_searcher_parses_mock_response() -> None:
    """MockTransport 下应把 results 解析为 WebResult。"""
    payload = {"results": [{"title": "标题", "url": "https://e.com", "content": "摘要"}]}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    searcher = TavilyWebSearcher(api_key="fake-key", transport=transport)
    results = searcher.search("查询")
    assert results[0].title == "标题"
    assert results[0].snippet == "摘要"


def test_pipeline_project_route_with_web_fallback() -> None:
    """作品库无证据时应触发 Web 兜底。"""
    empty_route = lambda query, project_id, top_k: []  # noqa: E731
    retriever = HybridRetriever(empty_route, vector_route=None)
    payload = {"results": [{"title": "兜底", "url": "u", "content": "c"}]}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    searcher = TavilyWebSearcher(api_key="fake-key", transport=transport)
    pipeline = RetrievalPipeline(retriever, searcher)
    route = RouteDecision(needs_project=True, needs_web=False)
    context = pipeline.run("张三的师父", route, None, resolve())
    assert context.chunks == []
    assert context.web_results[0].title == "兜底"


def test_pipeline_project_route_returns_reranked_chunks() -> None:
    """有证据时应返回精排后的 chunks，不触发 Web。"""
    hit_route = lambda query, project_id, top_k: [_chunk("c1", "张三拜青云子为师")]  # noqa: E731
    pipeline = RetrievalPipeline(HybridRetriever(hit_route, None), web_searcher=None)
    route = RouteDecision(needs_project=True)
    context = pipeline.run("张三的师父是谁", route, None, resolve())
    assert [chunk.chunk_id for chunk in context.chunks] == ["c1"]
    assert context.web_results == []
