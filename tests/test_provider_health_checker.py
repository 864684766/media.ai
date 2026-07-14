"""Provider 健康检查测试。"""

import pytest

from app.core.config import settings
from app.providers.provider_health_checker import check_provider_health


def test_provider_health_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """无 API Key 时应返回 configured=False，且不调用真实模型。"""
    monkeypatch.setattr(settings, "zhipu_api_key", None)
    result = check_provider_health()
    assert result.configured is False
    assert result.reachable is False
    assert "未配置 API Key" in result.message
