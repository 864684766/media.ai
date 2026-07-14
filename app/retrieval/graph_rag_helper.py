"""GraphRAG 与 Hybrid 结果合并辅助。"""

from app.core.runtime_config import RuntimeConfig
from app.retrieval.entity_extractor import extract_entities
from app.retrieval.graph_expander import expand_chunks_by_entities
from app.retrieval.retrieval_models import RetrievedChunk


def maybe_expand_chunks(
    question: str,
    chunks: list[RetrievedChunk],
    runtime_config: RuntimeConfig,
    project_id: str | None = None,
) -> list[RetrievedChunk]:
    """Hybrid 无结果时用图谱扩展兜底；已有证据时不扩展。"""
    if runtime_config.graph_expand_hops <= 0 or chunks:
        return chunks
    entities = extract_entities(question)
    expanded = expand_chunks_by_entities(
        entities,
        project_id=project_id,
        limit=runtime_config.rerank_top_k,
    )
    return _merge_unique(chunks, expanded)


def _merge_unique(
    base: list[RetrievedChunk],
    extra: list[RetrievedChunk],
) -> list[RetrievedChunk]:
    """按 chunk_id 去重合并。"""
    seen = {chunk.chunk_id for chunk in base}
    merged = list(base)
    for chunk in extra:
        if chunk.chunk_id and chunk.chunk_id not in seen:
            merged.append(chunk)
            seen.add(chunk.chunk_id)
    return merged
