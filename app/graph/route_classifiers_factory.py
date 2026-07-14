"""路由分类器统一工厂。

【职责】
    一次构建 L2 语义 + L3 LLM 分类器，供 deps / 组图注入。
"""

from app.graph.route_classifiers import RouteClassifiers
from app.graph.route_classifier_factory import build_route_classifier
from app.graph.semantic_classifier_factory import build_semantic_classifier


def build_route_classifiers() -> RouteClassifiers:
    """构建路由级联所需的全部分类器。

    返回:
        RouteClassifiers: 任一不可用则为 None，级联自动跳过该层。
    """
    return RouteClassifiers(
        semantic=build_semantic_classifier(),
        llm=build_route_classifier(),
    )
