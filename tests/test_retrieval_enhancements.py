"""Grader / Rewrite / Rerank / GraphRAG / 历史压缩 增强测试。"""

from app.graph.history_compactor import compact_history_if_needed
from app.graph.history_summarizer import TruncationSummarizer
from app.retrieval.entity_extractor import extract_entities
from app.retrieval.llm_grader_parser import parse_grader_response
from app.retrieval.project_route_runner import run_project_route
from app.retrieval.query_rewriter import PassthroughRewriter
from app.retrieval.rerank_factory import RuleRerankerAdapter
from app.retrieval.retrieval_constants import VERDICT_IRRELEVANT, VERDICT_RELEVANT
from app.retrieval.retrieval_models import GradeResult, RetrievedChunk
from app.retrieval.rule_grader import grade_by_rules
from app.schemas.agent_state import AgentState, ChatHistoryMessage, RouteDecision
from app.core.config_resolver import resolve


def _chunk(chunk_id: str, text: str) -> RetrievedChunk:
    """构造测试 chunk。"""
    return RetrievedChunk(chunk_id=chunk_id, text=text)


def test_parse_grader_json() -> None:
    """LLM Grader 解析合法 JSON。"""
    verdict = parse_grader_response('{"verdict":"relevant"}')
    assert verdict == VERDICT_RELEVANT


def test_rule_grader_irrelevant() -> None:
    """空证据应判 no_evidence（irrelevant 由 LLM Grader 在 hybrid 模式处理）。"""
    chunks = [_chunk("a", "师父")]
    result = grade_by_rules("张三的师父", chunks)
    assert result.verdict == VERDICT_RELEVANT


def test_rewrite_loop_with_passthrough() -> None:
    """irrelevant 时走 rewrite 回环。"""
    calls: list[str] = []

    def route(query: str, project_id: str | None, top_k: int) -> list[RetrievedChunk]:
        calls.append(query)
        if len(calls) >= 2:
            return [_chunk("hit", "张三拜青云子为师")]
        return [_chunk("miss", "无关")]

    class FakeRetriever:
        def retrieve(self, query: str, project_id: str | None, top_k: int) -> list[RetrievedChunk]:
            return route(query, project_id, top_k)

    class FakeGrader:
        def __init__(self) -> None:
            self.calls = 0

        def grade(self, question: str, chunks: list[RetrievedChunk]) -> GradeResult:
            self.calls += 1
            if self.calls >= 2:
                return GradeResult(verdict=VERDICT_RELEVANT)
            return GradeResult(verdict=VERDICT_IRRELEVANT)

    chunks, need_web = run_project_route(
        FakeRetriever(),
        "张三的师父",
        RouteDecision(needs_project=True),
        None,
        resolve(),
        FakeGrader(),
        RuleRerankerAdapter(),
        PassthroughRewriter(),
    )
    assert len(calls) == 2
    assert chunks[0].chunk_id == "hit"
    assert need_web is False


def test_entity_extractor() -> None:
    """应抽取中文实体候选。"""
    entities = extract_entities("张三的师父青云子是谁")
    assert any("张三" in entity for entity in entities)


def test_history_compactor_truncates() -> None:
    """超长历史应压缩并写入 summary。"""
    history = [
        ChatHistoryMessage(role="user", content=f"消息{i}" * 200)
        for i in range(10)
    ]
    state = AgentState(
        question="续写",
        conversation_id="c1",
        thread_id="c1",
        runtime_config=resolve(),
        history=history,
    )
    compacted = compact_history_if_needed(state, TruncationSummarizer())
    assert compacted.history_summary
    assert len(compacted.history) <= 6
