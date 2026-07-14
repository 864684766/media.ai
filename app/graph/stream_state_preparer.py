"""流式 Chat 的 State 准备器。

【职责】
    通过 LangGraph "准备图"执行 generate 之前的节点
    （load_skill → load_history → route_question → compact_history），
    得到可交给 Provider 流式接口的 prompt。

【为什么 generate 不在这张图里】
    SSE 需要把 Provider 每个 token 立即推给客户端；
    因此服务层（chat_stream_runner）直接消费 Provider 的流，
    图只负责准备 state，与 docs/ARCHITECTURE.html 15.5 的设计一致。
"""

from app.graph.graph_result_converter import to_agent_state
from app.graph.langgraph_builder import build_prepare_graph
from app.graph.route_classifiers import RouteClassifiers
from app.graph.state_factory import create_initial_state
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.schemas.agent_state import AgentState
from app.schemas.chat import ChatRequest
from app.storage.postgres.conversation_repository import ConversationRepository


def prepare_stream_state(
    request: ChatRequest,
    repository: ConversationRepository | None,
    retrieval_pipeline: RetrievalPipeline | None = None,
    route_classifiers: RouteClassifiers | None = None,
) -> AgentState:
    """执行 generate 前的节点。

    参数:
        request: Chat API 请求体。
        repository: 可选 PG Repository。
        retrieval_pipeline: 可选检索流水线；needs_project/web 时产出证据。
        route_classifiers: 可选路由级联分类器包。

    返回:
        AgentState: 已包含 skill/history/route/retrieval/prompt 的 state。
    """
    graph = build_prepare_graph(
        repository=repository,
        retrieval_pipeline=retrieval_pipeline,
        route_classifiers=route_classifiers,
    )
    result = graph.invoke(create_initial_state(request))
    return to_agent_state(result)
