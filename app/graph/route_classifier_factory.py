"""LLM 路由分类器工厂。

【职责】
    按 config/app.yaml route.mode 决定是否构建 LlmRouteClassifier：
    - mode=rules：返回 None（纯规则，不构建 Provider）
    - mode=llm / hybrid：尝试构建当前 Provider 并包装成分类器；
      构建失败（如无 API Key、配置缺失）返回 None，级联自动退化为纯规则。

【何时被调用】
    app/api/deps.py 组装 ChatService 时；脚本/测试也可直接调用。

【简例】
    build_route_classifier() -> LlmRouteClassifier | None
"""

import logging

from app.graph import route_cascade_constants as rc
from app.graph.llm_route_classifier import LlmRouteClassifier
from app.graph.route_settings_reader import RouteSettings, load_route_settings
from app.providers.registry import build_current_provider

logger = logging.getLogger(__name__)


def build_route_classifier(
    settings: RouteSettings | None = None,
) -> LlmRouteClassifier | None:
    """按配置构建 LLM 路由分类器。

    参数:
        settings: 可选路由配置；None 时读取 config/app.yaml。

    返回:
        LlmRouteClassifier | None: mode=rules 或 Provider 不可用时为 None。
    """
    route_settings = settings if settings is not None else load_route_settings()
    if route_settings.mode == rc.ROUTE_MODE_RULES:
        return None
    try:
        provider = build_current_provider()
    except Exception as exc:  # noqa: BLE001 — Provider 缺配置时退化为纯规则路由
        logger.warning("构建 LLM 路由分类器失败，退化为规则路由：%s", exc)
        return None
    return LlmRouteClassifier(provider)
