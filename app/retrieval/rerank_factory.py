"""Rerank 工厂。"""

from typing import Protocol

from app.ingestion import ingestion_constants as ic
from app.ingestion.embedder_factory import build_embedder
from app.ingestion.ingestion_settings import load_embedding_settings
from app.retrieval.rerank_settings_reader import (
    RERANK_PROVIDER_LOCAL,
    RERANK_PROVIDER_SEMANTIC,
    load_rerank_provider,
)
from app.retrieval.rule_reranker import rerank_by_rules
from app.retrieval.semantic_reranker import SemanticReranker
from app.retrieval.retrieval_models import RetrievedChunk
from app.retrieval.retrieval_protocols import ChunkReranker


class RuleRerankerAdapter:
    """规则 Rerank 适配器。"""

    def rerank(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        """调用规则版。"""
        return rerank_by_rules(question, chunks, top_k)


def build_reranker(yaml_config: dict | None = None) -> ChunkReranker:
    """按配置构建 Reranker。"""
    provider = load_rerank_provider(yaml_config)
    if provider == RERANK_PROVIDER_LOCAL:
        return RuleRerankerAdapter()
    settings = load_embedding_settings(yaml_config)
    embedder = build_embedder(
        provider=str(settings[ic.YAML_KEY_EMBEDDING_PROVIDER]),
        dimension=int(settings[ic.YAML_KEY_EMBEDDING_DIMENSION]),
    )
    return SemanticReranker(embedder)
