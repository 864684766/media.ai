"""规则版 Grader。

【职责】
    用词重叠分判断 relevant / no_evidence。
    irrelevant 由 LLM Grader（hybrid 模式）在规则不确定时补充。
"""

from app.retrieval.retrieval_constants import (
    GRADER_MIN_OVERLAP_SCORE,
    VERDICT_NO_EVIDENCE,
    VERDICT_RELEVANT,
)
from app.retrieval.retrieval_models import GradeResult, RetrievedChunk
from app.storage.postgres.keyword_scoring_helper import score_text, split_terms


def grade_by_rules(question: str, chunks: list[RetrievedChunk]) -> GradeResult:
    """规则评估证据相关性。"""
    if not chunks:
        return GradeResult(verdict=VERDICT_NO_EVIDENCE)
    terms = split_terms(question)
    best_score = max(score_text(chunk.text, terms) for chunk in chunks)
    if best_score >= GRADER_MIN_OVERLAP_SCORE:
        return GradeResult(verdict=VERDICT_RELEVANT)
    return GradeResult(verdict=VERDICT_NO_EVIDENCE)
