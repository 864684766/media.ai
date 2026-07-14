"""存储层单元测试（不依赖真实数据库）。"""

from unittest.mock import MagicMock

import pytest

from app.core.config import settings
from app.storage.neo4j.neo4j_health_checker import check_neo4j_health
from app.storage.postgres.postgres_engine_factory import create_postgres_engine
from app.storage.postgres.postgres_health_checker import check_postgres_health
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


@pytest.fixture
def clear_storage_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """测试前清空存储相关 .env，避免本机 .env 干扰。"""
    monkeypatch.setattr(settings, "database_url", None)
    monkeypatch.setattr(settings, "neo4j_uri", None)
    monkeypatch.setattr(settings, "neo4j_password", None)


def test_postgres_not_configured_by_default(clear_storage_env: None) -> None:
    """未设置 DATABASE_URL 时，应判定为未配置。"""
    assert is_postgres_configured() is False
    assert create_postgres_engine() is None


def test_postgres_health_when_not_configured(clear_storage_env: None) -> None:
    """未配置时 health 返回 configured=False，不抛异常。"""
    result = check_postgres_health()
    assert result.backend == "postgres"
    assert result.configured is False
    assert result.reachable is False


def test_neo4j_health_when_not_configured(clear_storage_env: None) -> None:
    """未配置 Neo4j 时 health 返回跳过说明。"""
    result = check_neo4j_health()
    assert result.backend == "neo4j"
    assert result.configured is False


def test_postgres_health_success_with_mock_engine() -> None:
    """Mock Engine 时 health 应返回 reachable=True。"""
    mock_conn = MagicMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    result = check_postgres_health(engine=mock_engine)
    assert result.configured is True
    assert result.reachable is True


def test_postgres_session_scope_raises_without_url(clear_storage_env: None) -> None:
    """未配置 URL 时使用 session scope 应抛出 RuntimeError。"""
    from app.storage.postgres.postgres_session_scope import postgres_session_scope

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        with postgres_session_scope(engine=None):
            pass
