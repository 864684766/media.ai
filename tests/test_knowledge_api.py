"""知识库 API 测试。"""

from fastapi.testclient import TestClient

from app.application import create_app


def test_knowledge_documents_empty_without_pg(monkeypatch) -> None:
    """未配置 PG 时返回空列表。"""
    monkeypatch.setattr(
        "app.api.knowledge.is_postgres_configured",
        lambda: False,
    )
    client = TestClient(create_app())
    response = client.get("/api/v1/knowledge/documents")
    assert response.status_code == 200
    assert response.json()["items"] == []
