"""Hybrid 检索器与检索流水线工厂。

【职责】
    按 .env 与 config/app.yaml 组装生产用的检索依赖：
    - 关键词路：PG Session + ChunkKeywordSearcher
    - 向量路：Neo4j Driver + 向量索引 kNN + Embedder
    - Web 路：TavilyWebSearcher（读 web_search 配置与 TAVILY_API_KEY）
    某一依赖未配置时对应路自动缺席，检索链整体仍可运行。

【何时被调用】
    app/api/deps.py 在处理请求时组装 RetrievalPipeline。

【简例】
    pipeline = build_retrieval_pipeline(session)   # session 可为 None
"""

import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.ingestion import ingestion_constants as ic
from app.ingestion.embedder_factory import build_embedder
from app.ingestion.ingestion_settings import load_embedding_settings
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.retrieval_models import RetrievedChunk
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.retrieval.web_search import TavilyWebSearcher
from app.retrieval.web_search_settings_reader import (
    YAML_KEY_MAX_RESULTS,
    load_web_search_settings,
)
from app.storage.neo4j import neo4j_constants as nc
from app.storage.neo4j.neo4j_driver_factory import create_neo4j_driver
from app.storage.neo4j.neo4j_vector_index import query_similar_chunks
from app.storage.postgres.chunk_keyword_searcher import ChunkKeywordSearcher

# 单路检索函数签名（与 hybrid.SearchRoute 一致）
SearchRoute = Callable[[str, str | None, int], list[RetrievedChunk]]


def build_retrieval_pipeline(session: Session | None) -> RetrievalPipeline:
    """组装完整检索流水线。

    参数:
        session: 可选 PG Session（来自请求级依赖注入）；None 时关键词路缺席。

    返回:
        RetrievalPipeline: 可直接 run 的流水线。
    """
    keyword_route = _build_keyword_route(session) if session is not None else None
    vector_route = _build_vector_route()
    retriever = None
    if keyword_route is not None or vector_route is not None:
        retriever = HybridRetriever(keyword_route, vector_route)
    return RetrievalPipeline(retriever, _build_web_searcher())


def _build_keyword_route(session: Session) -> SearchRoute:
    """构造关键词路：PG chunks 表 LIKE 打分。"""
    searcher = ChunkKeywordSearcher(session)

    def route(query: str, project_id: str | None, top_k: int) -> list[RetrievedChunk]:
        """执行关键词召回并转成 RetrievedChunk。"""
        pairs = searcher.search(query, project_id, top_k)
        return [
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                score=score,
                source=chunk.source,
            )
            for chunk, score in pairs
        ]

    return route


def _build_vector_route() -> SearchRoute | None:
    """构造向量路：Neo4j kNN；未配置 Neo4j 时返回 None。"""
    driver = create_neo4j_driver()
    if driver is None:
        return None
    settings = load_embedding_settings()
    embedder = build_embedder(
        provider=str(settings[ic.YAML_KEY_EMBEDDING_PROVIDER]),
        dimension=int(settings[ic.YAML_KEY_EMBEDDING_DIMENSION]),
    )

    def route(query: str, project_id: str | None, top_k: int) -> list[RetrievedChunk]:
        """向量化查询词并做 kNN 近邻检索。

        Neo4j 查询失败（如向量索引未创建、连接中断）时返回空列表，
        让 Hybrid 退化为关键词单路，不打断整个 Chat 请求。
        """
        [embedding] = embedder.embed_texts([query])
        try:
            rows = query_similar_chunks(driver, embedding, top_k, project_id)
        except Exception as exc:  # noqa: BLE001 — 向量路故障必须降级而非中断对话
            logger.warning("Neo4j 向量检索失败，降级为关键词单路: %s", exc)
            return []
        return [
            RetrievedChunk(
                chunk_id=str(row.get(nc.KNN_COLUMN_CHUNK_ID, "")),
                text=str(row.get(nc.KNN_COLUMN_TEXT, "")),
                score=float(row.get(nc.KNN_COLUMN_SCORE, 0.0)),
                source=str(row.get(nc.KNN_COLUMN_SOURCE, "")),
            )
            for row in rows
        ]

    return route


def _build_web_searcher() -> TavilyWebSearcher:
    """按 config/app.yaml web_search 段构造搜索器（Key 缺失时自动降级）。"""
    settings = load_web_search_settings()
    return TavilyWebSearcher(max_results=settings[YAML_KEY_MAX_RESULTS])
