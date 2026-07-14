"""neo4j_driver_singleton 单元测试。"""

from app.storage.neo4j.neo4j_driver_factory import create_neo4j_driver
from app.storage.neo4j.neo4j_driver_singleton import (
    get_shared_neo4j_driver,
    reset_shared_neo4j_driver,
)


def test_create_neo4j_driver_returns_same_instance(monkeypatch) -> None:
    """多次调用应返回同一 Driver 实例。"""
    monkeypatch.setenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    monkeypatch.setenv("NEO4J_PASSWORD", "secret")
    reset_shared_neo4j_driver()
    first = create_neo4j_driver()
    second = get_shared_neo4j_driver()
    assert first is not None
    assert first is second
    reset_shared_neo4j_driver()
