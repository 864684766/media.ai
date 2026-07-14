"""Hybrid 检索器（关键词路 + 向量路 → RRF）。

【职责】
    docs/ARCHITECTURE.html sec-06「Hybrid 检索 = 向量 + 关键词 → RRF」。
    - 关键词路：PG chunks 表 LIKE 打分（ChunkKeywordSearcher）
    - 向量路：Neo4j 向量索引 kNN（query_similar_chunks）
    两路各取 top_k，按 chunk_id 去重 RRF 融合。

【依赖注入】
    两路检索函数均可注入替换（测试用假函数；生产由
    app/retrieval/hybrid_factory.py 按 .env 组装）。
    某一路不可用（未配置对应数据库）时自动退化为单路检索。

【简例】
    retriever = HybridRetriever(keyword_search, vector_search)
    chunks = retriever.retrieve("张三的师父是谁", project_id="demo", top_k=30)
"""

from collections.abc import Callable

from app.retrieval.retrieval_models import RetrievedChunk
from app.retrieval.rrf import fuse_ranked_lists

# 单路检索函数签名：(query, project_id, top_k) -> 有序 RetrievedChunk 列表
SearchRoute = Callable[[str, str | None, int], list[RetrievedChunk]]


class HybridRetriever:
    """两路召回 + RRF 融合。

    参数说明:
        keyword_route: 关键词路检索函数；None 表示该路不可用。
        vector_route: 向量路检索函数；None 表示该路不可用。
    """

    def __init__(
        self,
        keyword_route: SearchRoute | None,
        vector_route: SearchRoute | None,
    ) -> None:
        """登记两路检索函数。"""
        self._keyword_route = keyword_route
        self._vector_route = vector_route

    def retrieve(
        self,
        query: str,
        project_id: str | None,
        top_k: int,
    ) -> list[RetrievedChunk]:
        """执行 Hybrid 检索。

        参数:
            query: 查询文本（route_question 的 sub_query 或原问题）。
            project_id: 项目过滤；None 时不过滤。
            top_k: 每路最多召回条数。

        返回:
            list[RetrievedChunk]: RRF 融合后的证据列表（可能为空）。
        """
        ranked_lists = [
            route(query, project_id, top_k)
            for route in (self._keyword_route, self._vector_route)
            if route is not None
        ]
        if not ranked_lists:
            return []
        return fuse_ranked_lists(ranked_lists)
