"""Grader 工厂与混合策略。"""

from typing import Protocol

from app.retrieval import grader_constants as gc
from app.retrieval.grader_settings_reader import load_grader_mode
from app.retrieval.llm_grader import LlmGrader
from app.retrieval.retrieval_constants import VERDICT_IRRELEVANT, VERDICT_RELEVANT
from app.retrieval.retrieval_models import GradeResult, RetrievedChunk
from app.retrieval.retrieval_protocols import ChunkGrader
from app.retrieval.rule_grader import grade_by_rules
from app.retrieval.chat_provider_factory import build_chat_provider


class RuleChunkGrader:
    """规则 Grader 适配器。"""

    def grade(self, question: str, chunks: list[RetrievedChunk]) -> GradeResult:
        """调用规则版。"""
        return grade_by_rules(question, chunks)


class HybridChunkGrader:
    """混合 Grader：规则优先，边界情况问 LLM。"""

    def __init__(self, llm: LlmGrader) -> None:
        """绑定 LLM Grader。"""
        self._llm = llm

    def grade(self, question: str, chunks: list[RetrievedChunk]) -> GradeResult:
        """规则 → 必要时 LLM。"""
        rule_result = grade_by_rules(question, chunks)
        if rule_result.verdict in (VERDICT_RELEVANT, VERDICT_IRRELEVANT):
            return rule_result
        llm_result = self._llm.grade(question, chunks)
        return llm_result if llm_result is not None else rule_result


def build_grader(yaml_config: dict | None = None) -> ChunkGrader:
    """按配置构建 Grader。

    参数:
        yaml_config: 测试可传入假 app.yaml。

    返回:
        ChunkGrader: 规则 / LLM / 混合实现。
    """
    mode = load_grader_mode(yaml_config)
    if mode == gc.GRADER_MODE_RULE:
        return RuleChunkGrader()
    provider = build_chat_provider(yaml_config)
    llm = LlmGrader(provider)
    if mode == gc.GRADER_MODE_LLM:
        return _LlmAdapter(llm)
    return HybridChunkGrader(llm)


class _LlmAdapter:
    """LLM Grader 包装：失败回退规则。"""

    def __init__(self, llm: LlmGrader) -> None:
        """绑定 LLM。"""
        self._llm = llm

    def grade(self, question: str, chunks: list[RetrievedChunk]) -> GradeResult:
        """LLM 优先，失败回退规则。"""
        result = self._llm.grade(question, chunks)
        return result if result is not None else grade_by_rules(question, chunks)
