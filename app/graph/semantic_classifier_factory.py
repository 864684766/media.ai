"""语义路由分类器工厂。

【职责】
    按 route.mode 与 embedding 配置构造 SemanticRouteClassifier；
    embedder 不可用时返回 None，级联自动跳过 L2。
"""

import logging

from app.graph.semantic_route_classifier import SemanticRouteClassifier
from app.ingestion.embedder_factory import build_embedder
from app.ingestion.ingestion_settings import load_embedding_settings

logger = logging.getLogger(__name__)


def build_semantic_classifier() -> SemanticRouteClassifier | None:
    """构建语义路由分类器。

    返回:
        SemanticRouteClassifier | None: hashing 等弱语义 embedder 仍可用但效果有限。
    """
    try:
        settings = load_embedding_settings()
        embedder = build_embedder(
            provider=str(settings["provider"]),
            dimension=int(settings["dimension"]),
        )
        return SemanticRouteClassifier(embedder=embedder)
    except Exception as exc:  # noqa: BLE001
        logger.warning("语义路由分类器构建失败: %s", exc)
        return None
