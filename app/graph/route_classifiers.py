"""路由级联所需分类器集合。

【职责】
    把 L2 语义分类器与 L3 LLM 分类器打包，便于组图时一次注入 route_question 节点。
"""

from dataclasses import dataclass

from app.graph.llm_route_classifier import LlmRouteClassifier
from app.graph.semantic_route_classifier import SemanticRouteClassifier


@dataclass(frozen=True)
class RouteClassifiers:
    """路由级联分类器包。

    参数说明:
        semantic: L2 语义路由（可选）。
        llm: L3 LLM 结构化路由（可选）。
    """

    semantic: SemanticRouteClassifier | None = None
    llm: LlmRouteClassifier | None = None
