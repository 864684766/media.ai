"""规则版 Rerank（词重叠 + RRF 分）。"""

from app.retrieval.retrieval_models import RetrievedChunk
from app.storage.postgres.keyword_scoring_helper import score_text, split_terms


def rerank_by_rules(
    question: str,
    chunks: list[RetrievedChunk],
    top_k: int,
) -> list[RetrievedChunk]:
    """规则精排并截断。"""
    terms = split_terms(question)
    rescored = [
        chunk.model_copy(update={"score": score_text(chunk.text, terms) + chunk.score})
        for chunk in chunks
    ]
    rescored.sort(key=lambda chunk: chunk.score, reverse=True)
    return rescored[:top_k]
