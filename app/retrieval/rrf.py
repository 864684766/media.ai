"""RRF（Reciprocal Rank Fusion）融合。

【职责】
    把关键词路与向量路两份「有序候选列表」融合成一份，
    按 chunk_id 去重（sec-04.7 Chunk ID 对齐是前提）。

【原理（初学者向）】
    每条候选在各自列表中的名次 rank（从 1 起），
    融合分 = Σ 1 / (RRF_K + rank)。
    两路都靠前的 chunk 分数最高；只在一路出现也能拿到分数。
    RRF 只看名次不看原始分，天然规避「两路打分量纲不同」的问题。

【简例】
    fuse_ranked_lists([[c1, c2], [c2, c3]]) -> [c2, c1, c3]（c2 两路都有，最靠前）
"""

from app.retrieval.retrieval_constants import RRF_K
from app.retrieval.retrieval_models import RetrievedChunk


def fuse_ranked_lists(ranked_lists: list[list[RetrievedChunk]]) -> list[RetrievedChunk]:
    """融合多份有序候选列表。

    参数:
        ranked_lists: 每路召回的有序结果（越靠前越相关）。

    返回:
        list[RetrievedChunk]: 融合去重后按 RRF 分数降序的列表，
        score 字段替换为 RRF 分数。
    """
    scores: dict[str, float] = {}
    chunk_by_id: dict[str, RetrievedChunk] = {}
    for ranked in ranked_lists:
        _accumulate(ranked, scores, chunk_by_id)
    fused = [
        chunk_by_id[chunk_id].model_copy(update={"score": score})
        for chunk_id, score in scores.items()
    ]
    fused.sort(key=lambda chunk: chunk.score, reverse=True)
    return fused


def _accumulate(
    ranked: list[RetrievedChunk],
    scores: dict[str, float],
    chunk_by_id: dict[str, RetrievedChunk],
) -> None:
    """把一路结果累加进融合分数表。

    参数:
        ranked: 单路有序结果。
        scores: chunk_id -> 累计 RRF 分。
        chunk_by_id: chunk_id -> chunk 对象（首次出现登记）。
    """
    for rank, chunk in enumerate(ranked, start=1):
        scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (RRF_K + rank)
        chunk_by_id.setdefault(chunk.chunk_id, chunk)
