"""依赖注入辅助方法。

【职责】
    集中管理路由层使用的依赖工厂，避免 API 文件直接创建数据库连接。

【数据库策略】
    未配置 DATABASE_URL → repository=None，本地仍可调用 Chat API；
    已配置 DATABASE_URL → 为本次请求创建 Session + ConversationRepository。

【检索策略】
    检索流水线按可用依赖自动降级：
    PG 有则带关键词路；Neo4j 有则带向量路；TAVILY_API_KEY 有则可联网。

【路由策略】
    route.mode=hybrid/llm 且 Provider 可用 → 注入 LLM 路由分类器；
    否则分类器为 None，级联自动退化为纯规则路由。
"""

from collections.abc import Iterator

from fastapi import Depends

from app.graph.route_classifiers import RouteClassifiers
from app.graph.route_classifiers_factory import build_route_classifiers
from app.retrieval.hybrid_factory import build_retrieval_pipeline
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.services.chat import ChatService
from app.storage.postgres.conversation_repository import ConversationRepository
from app.storage.postgres.postgres_session_scope import postgres_session_scope
from app.storage.postgres.postgres_settings_reader import is_postgres_configured


def get_postgres_repository() -> Iterator[ConversationRepository | None]:
    """创建可选 PostgreSQL Repository。

    yields:
        ConversationRepository | None: 未配置 DATABASE_URL 时为 None。
    """
    if not is_postgres_configured():
        yield None
        return
    with postgres_session_scope() as session:
        yield ConversationRepository(session)


def get_retrieval_pipeline() -> Iterator[RetrievalPipeline]:
    """创建检索流水线（含请求级 PG Session 生命周期管理）。

    yields:
        RetrievalPipeline: 按可用依赖组装的流水线（依赖缺失时自动降级）。
    """
    if not is_postgres_configured():
        yield build_retrieval_pipeline(session=None)
        return
    with postgres_session_scope() as session:
        yield build_retrieval_pipeline(session=session)


def get_route_classifiers() -> RouteClassifiers:
    """构建路由级联分类器包（L2 语义 + L3 LLM）。

    返回:
        RouteClassifiers: 任一层不可用则为 None，级联自动跳过。
    """
    return build_route_classifiers()


def get_chat_service(
    repository: ConversationRepository | None = Depends(get_postgres_repository),
    retrieval_pipeline: RetrievalPipeline = Depends(get_retrieval_pipeline),
    route_classifiers: RouteClassifiers = Depends(get_route_classifiers),
) -> ChatService:
    """构造 ChatService 实例。

    参数:
        repository: 可选 ConversationRepository。
        retrieval_pipeline: 检索流水线。
        route_classifiers: 路由级联分类器包。

    返回:
        ChatService: 注入到路由的服务实例。
    """
    return ChatService(
        repository=repository,
        retrieval_pipeline=retrieval_pipeline,
        route_classifiers=route_classifiers,
    )
