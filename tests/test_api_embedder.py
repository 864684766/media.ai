"""智谱 API Embedder 测试。

【覆盖点】
    1. MockTransport 下解析 embedding 响应。
    2. 无 API Key 时抛 RuntimeError。
    3. build_embedder(zhipu) 无 Key 时回退 hashing。
"""

import httpx

from app.ingestion.api_embedder import ZhipuApiEmbedder
from app.ingestion.embedder import HashingEmbedder
from app.ingestion.embedder_factory import build_embedder
from app.ingestion import ingestion_constants as ic


def test_zhipu_embedder_parses_mock_response(monkeypatch) -> None:
    """Mock embeddings API 应返回解析后的向量。"""
    monkeypatch.setenv("ZHIPU_API_KEY", "fake-key")
    payload = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    embedder = ZhipuApiEmbedder(dimension=3, client=httpx.Client(transport=transport))
    vectors = embedder.embed_texts(["测试文本"])
    assert vectors[0] == [0.1, 0.2, 0.3]


def test_zhipu_embedder_without_key_raises(monkeypatch) -> None:
    """未配置 Key 时 embed_texts 应抛 RuntimeError。"""
    monkeypatch.setattr(
        "app.ingestion.api_embedder.load_model_config",
        lambda: type("Cfg", (), {"api_key": "", "api_base": "http://x"})(),
    )
    embedder = ZhipuApiEmbedder(dimension=3)
    try:
        embedder.embed_texts(["测试"])
        raised = False
    except RuntimeError:
        raised = True
    assert raised


def test_build_embedder_zhipu_fallback_without_key(monkeypatch) -> None:
    """zhipu provider 无 Key 时应回退 HashingEmbedder。"""
    monkeypatch.setattr(
        "app.ingestion.embedder_factory._has_zhipu_api_key",
        lambda: False,
    )
    embedder = build_embedder(provider=ic.EMBEDDING_PROVIDER_ZHIPU, dimension=64)
    assert isinstance(embedder, HashingEmbedder)
