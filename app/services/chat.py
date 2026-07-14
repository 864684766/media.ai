"""Chat 业务服务。

【职责】
    POST 调用 LangGraph 对话图并输出 SSE 流式事件。
"""

from collections.abc import Iterable

from app.graph.route_classifiers import RouteClassifiers
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.schemas.chat import ChatRequest
from app.services.chat_stream_runner import stream_chat_frames
from app.storage.postgres.conversation_repository import ConversationRepository


class ChatService:
    """Chat 业务服务。

    参数说明:
        repository: 可选 PG Repository；为空时不落库，便于本地无数据库开发。
        retrieval_pipeline: 可选检索流水线；为空时跳过 RAG/Web，仅创作路径。
        route_classifiers: 可选路由级联分类器包；为空时纯规则路由。
    """

    def __init__(
        self,
        repository: ConversationRepository | None = None,
        retrieval_pipeline: RetrievalPipeline | None = None,
        route_classifiers: RouteClassifiers | None = None,
    ) -> None:
        """初始化 ChatService。"""
        self._repository = repository
        self._retrieval_pipeline = retrieval_pipeline
        self._route_classifiers = route_classifiers

    def stream_chat(self, request: ChatRequest) -> Iterable[str]:
        """执行 Chat 图并返回 SSE 文本帧。

        参数:
            request: Chat API 请求体。

        返回:
            Iterable[str]: SSE 帧文本序列。
        """
        return stream_chat_frames(
            request,
            repository=self._repository,
            retrieval_pipeline=self._retrieval_pipeline,
            route_classifiers=self._route_classifiers,
        )
