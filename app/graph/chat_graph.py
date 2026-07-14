"""Chat 对话图入口（真实 LangGraph StateGraph）。

【职责】
    对外提供 run_minimal_chat_graph：一次性执行完整对话图并返回终态。
    图结构组装在 app/graph/langgraph_builder.py，本文件只负责调用。

【执行顺序】
    create_initial_state → load_skill → load_history → route_question
    → compact_history → generate → save_messages

【何时被调用】
    - 测试（tests/test_chat_graph.py）
    - 非流式场景 / 脚本
    SSE 流式路径不走本函数，见 app/services/chat_stream_runner.py。
"""

from app.graph.graph_result_converter import to_agent_state
from app.graph.langgraph_builder import build_chat_graph
from app.graph.route_classifiers import RouteClassifiers
from app.graph.nodes.generate import Responder
from app.graph.state_factory import create_initial_state
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.schemas.agent_state import AgentState
from app.schemas.chat import ChatRequest
from app.storage.postgres.conversation_repository import ConversationRepository


def run_minimal_chat_graph(
    request: ChatRequest,
    responder: Responder | None = None,
    repository: ConversationRepository | None = None,
    retrieval_pipeline: RetrievalPipeline | None = None,
    route_classifiers: RouteClassifiers | None = None,
) -> AgentState:
    """执行完整 Chat 图（LangGraph invoke）。

    参数:
        request: Chat API 请求体。
        responder: 可选生成函数，测试中注入。
        repository: 可选 PG Repository，注入后读写真实会话消息。
        retrieval_pipeline: 可选检索流水线，注入后启用 RAG/Web 证据。
        route_classifiers: 可选路由级联分类器包。

    返回:
        AgentState: 图执行结束后的状态。
    """
    graph = build_chat_graph(
        responder=responder,
        repository=repository,
        retrieval_pipeline=retrieval_pipeline,
        route_classifiers=route_classifiers,
    )
    result = graph.invoke(create_initial_state(request))
    return to_agent_state(result)
