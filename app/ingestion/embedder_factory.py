"""Embedder 工厂。

【职责】
    按 ingestion.embedding.provider 构造具体 Embedder；
    API 不可用或 provider 未知时回退 HashingEmbedder，保证流水线不中断。
"""

import logging

from app.ingestion import ingestion_constants as ic
from app.ingestion.api_embedder import ZhipuApiEmbedder
from app.ingestion.embedder import Embedder, HashingEmbedder

logger = logging.getLogger(__name__)


def build_embedder(
    provider: str = ic.DEFAULT_EMBEDDING_PROVIDER,
    dimension: int = ic.DEFAULT_EMBEDDING_DIMENSION,
) -> Embedder:
    """按配置构造 Embedder（含 API 失败回退）。

    参数:
        provider: hashing / zhipu。
        dimension: 向量维度。

    返回:
        Embedder: 实现实例。
    """
    if provider == ic.EMBEDDING_PROVIDER_ZHIPU:
        return _try_zhipu_embedder(dimension)
    if provider == ic.EMBEDDING_PROVIDER_HASHING:
        return HashingEmbedder(dimension=dimension)
    logger.warning("未知 embedding provider=%s，回退 hashing", provider)
    return HashingEmbedder(dimension=dimension)


def _try_zhipu_embedder(dimension: int) -> Embedder:
    """尝试构造智谱 API embedder；无 Key 或失败则回退 hashing。"""
    if not _has_zhipu_api_key():
        logger.warning("ZHIPU_API_KEY 未配置，回退 hashing")
        return HashingEmbedder(dimension=dimension)
    try:
        return ZhipuApiEmbedder(dimension=dimension)
    except Exception as exc:  # noqa: BLE001 — 缺 Key 等场景必须降级
        logger.warning("API embedder 不可用，回退 hashing: %s", exc)
        return HashingEmbedder(dimension=dimension)


def _has_zhipu_api_key() -> bool:
    """检查是否配置了智谱 API Key。"""
    from app.providers.provider_settings_reader import load_model_config

    return bool(load_model_config().api_key)
