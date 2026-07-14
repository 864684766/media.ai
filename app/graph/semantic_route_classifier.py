"""L2 语义路由分类器。

【职责】
    将用户问题与预置意图示例句做 embedding 余弦相似度匹配，
    输出 RouteDecision（比关键词更抗「换说法」，比 LLM 更快更省）。

【依赖】
    需要真实语义 embedder（zhipu）；构造失败时 classify 返回 None，级联自动跳过。
"""

import logging
from dataclasses import dataclass

from app.graph.cosine_similarity_helper import cosine_similarity
from app.graph.route_domain_helper import resolve_domain
from app.graph import semantic_route_constants as sc
from app.ingestion.embedder import Embedder
from app.schemas.agent_state import RouteDecision

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _IntentRoute:
    """单条意图路由定义。"""

    name: str
    utterances: tuple[str, ...]
    needs_project: bool
    needs_web: bool
    needs_creative: bool


_INTENT_ROUTES: tuple[_IntentRoute, ...] = (
    _IntentRoute(sc.INTENT_PROJECT, sc.PROJECT_UTTERANCES, True, False, True),
    _IntentRoute(sc.INTENT_WEB, sc.WEB_UTTERANCES, False, True, False),
    _IntentRoute(sc.INTENT_CREATIVE, sc.CREATIVE_UTTERANCES, False, False, True),
)


class SemanticRouteClassifier:
    """语义路由分类器。

    参数说明:
        embedder: 语义向量化器（zhipu 或 hashing）。
        threshold: 相似度阈值，低于则不命中。
    """

    def __init__(
        self,
        embedder: Embedder,
        threshold: float = sc.DEFAULT_SEMANTIC_THRESHOLD,
    ) -> None:
        """初始化并预计算示例句向量。"""
        self._embedder = embedder
        self._threshold = threshold
        self._route_vectors = self._build_route_vectors()

    def classify(self, question: str) -> RouteDecision | None:
        """语义匹配路由。

        参数:
            question: 用户问题。

        返回:
            RouteDecision | None: 命中返回决策；未达阈值返回 None。
        """
        try:
            [query_vec] = self._embedder.embed_texts([question])
        except Exception as exc:  # noqa: BLE001
            logger.warning("语义路由 embedding 失败: %s", exc)
            return None
        return self._match_best_route(query_vec, question)

    def _build_route_vectors(self) -> list[tuple[_IntentRoute, list[list[float]]]]:
        """预计算各意图示例句向量。"""
        result: list[tuple[_IntentRoute, list[list[float]]]] = []
        for route in _INTENT_ROUTES:
            vectors = self._embedder.embed_texts(list(route.utterances))
            result.append((route, vectors))
        return result

    def _match_best_route(
        self,
        query_vec: list[float],
        question: str,
    ) -> RouteDecision | None:
        """取最高相似度意图；未达阈值返回 None。"""
        best_score = 0.0
        best_route: _IntentRoute | None = None
        for route, vectors in self._route_vectors:
            score = max(cosine_similarity(query_vec, vec) for vec in vectors)
            if score > best_score:
                best_score = score
                best_route = route
        if best_route is None or best_score < self._threshold:
            return None
        return _to_decision(best_route, question, best_score)


def _to_decision(route: _IntentRoute, question: str, score: float) -> RouteDecision:
    """意图路由转 RouteDecision。"""
    return RouteDecision(
        domain=resolve_domain(route.needs_project, route.needs_web, route.needs_creative),
        needs_project=route.needs_project,
        needs_web=route.needs_web,
        needs_creative=route.needs_creative,
        sub_queries=[question] if route.needs_project else [],
        confidence=sc.SEMANTIC_ROUTE_CONFIDENCE,
        reason=f"{sc.SEMANTIC_ROUTE_REASON}（{route.name}，相似度 {score:.2f}）",
    )
