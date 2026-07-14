"""智谱 OpenAI 兼容 Embedding API 客户端。

【职责】
    调用 {api_base}/embeddings 将文本转为语义向量，供 Neo4j 向量检索与语义路由使用。
    无 API Key 或请求失败时由 build_embedder 回退 HashingEmbedder。

【何时被调用】
    build_embedder(provider="zhipu") 时构造本类实例。
"""

import logging
from typing import Any

import httpx

from app.ingestion import embedding_constants as ec
from app.providers import provider_constants as pc
from app.providers.provider_settings_reader import load_model_config

logger = logging.getLogger(__name__)


class ZhipuApiEmbedder:
    """智谱 API Embedder。

    参数说明:
        dimension: 期望向量维度（与 Neo4j 索引一致；embedding-2 为 1024）。
        client: 可选 httpx.Client；测试注入 MockTransport。
    """

    def __init__(
        self,
        dimension: int = ec.ZHIPU_EMBEDDING_DIMENSION,
        client: httpx.Client | None = None,
    ) -> None:
        """初始化并记录维度。"""
        self.dimension = dimension
        self._config = load_model_config()
        self._client = client if client is not None else httpx.Client(timeout=30.0)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量向量化。

        参数:
            texts: 文本列表。

        返回:
            list[list[float]]: 与输入一一对应的向量。

        异常:
            RuntimeError: 未配置 API Key 或 HTTP 失败时抛出。
        """
        if not self._config.api_key:
            raise RuntimeError("ZHIPU_API_KEY 未配置，无法使用 API embedder")
        payload = self._build_payload(texts)
        vectors = self._post_embeddings(payload)
        return [_fit_dimension(vector, self.dimension) for vector in vectors]

    def _build_payload(self, texts: list[str]) -> dict[str, Any]:
        """构造 OpenAI 兼容 embedding 请求体。"""
        return {
            ec.EMBEDDING_FIELD_MODEL: ec.ZHIPU_EMBEDDING_MODEL,
            ec.EMBEDDING_FIELD_INPUT: texts,
        }

    def _post_embeddings(self, payload: dict[str, Any]) -> list[list[float]]:
        """POST embeddings 并解析向量列表。"""
        url = f"{self._config.api_base.rstrip('/')}{ec.ZHIPU_EMBEDDINGS_PATH}"
        headers = {pc.CONTENT_TYPE_HEADER_NAME: pc.JSON_CONTENT_TYPE}
        if self._config.api_key:
            headers[pc.AUTHORIZATION_HEADER_NAME] = f"{pc.BEARER_TOKEN_PREFIX} {self._config.api_key}"
        response = self._client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return _parse_embedding_response(response.json())


def _fit_dimension(vector: list[float], dimension: int) -> list[float]:
    """将向量调整到目标维度。"""
    if len(vector) == dimension:
        return vector
    if len(vector) > dimension:
        return vector[:dimension]
    return vector + [0.0] * (dimension - len(vector))


def _parse_embedding_response(raw: dict[str, Any]) -> list[list[float]]:
    """从 OpenAI 兼容响应解析 embedding 数组。"""
    data = raw.get(ec.EMBEDDING_FIELD_DATA, [])
    if not isinstance(data, list):
        return []
    vectors: list[list[float]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        embedding = item.get(ec.EMBEDDING_FIELD_EMBEDDING)
        if isinstance(embedding, list):
            vectors.append([float(v) for v in embedding])
    return vectors
