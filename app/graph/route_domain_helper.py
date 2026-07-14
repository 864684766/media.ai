"""RouteDecision.domain 推导辅助。

【职责】
    根据三个能力开关推导 domain 兼容字段（sec-15 契约）。
    规则层（route_rules.py）与 LLM 层（llm_route_parser.py）共用，避免口径漂移。

【简例】
    resolve_domain(True, False, True) -> "composite"
"""

from app.graph.route_rule_constants import (
    DOMAIN_COMPOSITE,
    DOMAIN_GENERAL,
    DOMAIN_PROJECT,
    DOMAIN_REALTIME,
)


def resolve_domain(needs_project: bool, needs_web: bool, needs_creative: bool) -> str:
    """根据开关组合推导 domain。

    参数:
        needs_project: 是否查作品库。
        needs_web: 是否联网。
        needs_creative: 是否创作。

    返回:
        str: general / project / realtime / composite。
    """
    enabled = sum([needs_project, needs_web, needs_creative])
    if enabled > 1:
        return DOMAIN_COMPOSITE
    if needs_project:
        return DOMAIN_PROJECT
    if needs_web:
        return DOMAIN_REALTIME
    return DOMAIN_GENERAL
