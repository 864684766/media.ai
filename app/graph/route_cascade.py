"""路由级联编排（Routing Cascade）。

【职责】
    L1 规则 → L2 语义 → L3 LLM 分层升级（docs/ARCHITECTURE.html sec-07 7.2）。
    任一层失败回退上一层结果，路由永不阻塞主流程。
"""

from app.graph import route_cascade_constants as rc
from app.graph.route_classifiers import RouteClassifiers
from app.graph.route_rules import infer_route_decision
from app.graph.route_settings_reader import RouteSettings, load_route_settings
from app.schemas.agent_state import RouteDecision


def decide_route(
    question: str,
    classifiers: RouteClassifiers | None = None,
    settings: RouteSettings | None = None,
) -> RouteDecision:
    """级联路由决策入口。

    参数:
        question: 用户问题原文。
        classifiers: 可选 L2/L3 分类器包。
        settings: 可选路由配置。

    返回:
        RouteDecision: 最终路由决策。
    """
    route_settings = settings if settings is not None else load_route_settings()
    bundle = classifiers if classifiers is not None else RouteClassifiers()
    rule_decision = infer_route_decision(question, keywords=route_settings.keywords)
    if not _needs_upgrade(rule_decision, route_settings):
        return rule_decision
    semantic_decision = _try_semantic(question, bundle, route_settings)
    if semantic_decision is not None:
        return semantic_decision
    llm_decision = _try_llm(question, bundle, route_settings)
    if llm_decision is not None:
        return llm_decision
    return _mark_fallback(rule_decision)


def _needs_upgrade(decision: RouteDecision, settings: RouteSettings) -> bool:
    """规则层置信度是否不足以直接采用。"""
    if settings.mode == rc.ROUTE_MODE_RULES:
        return False
    if settings.mode == rc.ROUTE_MODE_LLM:
        return True
    return decision.confidence < settings.llm_confidence_threshold


def _try_semantic(
    question: str,
    bundle: RouteClassifiers,
    settings: RouteSettings,
) -> RouteDecision | None:
    """L2 语义路由；rules 模式跳过。"""
    if settings.mode == rc.ROUTE_MODE_RULES or bundle.semantic is None:
        return None
    return bundle.semantic.classify(question)


def _try_llm(
    question: str,
    bundle: RouteClassifiers,
    settings: RouteSettings,
) -> RouteDecision | None:
    """L3 LLM 路由；需 mode=llm 或 hybrid 且 L2 未命中。"""
    if bundle.llm is None or settings.mode == rc.ROUTE_MODE_RULES:
        return None
    if settings.mode == rc.ROUTE_MODE_HYBRID and bundle.semantic is not None:
        pass
    return bundle.llm.classify(question)


def _mark_fallback(rule_decision: RouteDecision) -> RouteDecision:
    """高层失败时标注回退原因。"""
    return rule_decision.model_copy(
        update={"reason": rule_decision.reason + rc.LLM_FALLBACK_REASON_SUFFIX},
    )
