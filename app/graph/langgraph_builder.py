"""LangGraph StateGraph 组图器。

【职责】
    用真实的 langgraph.StateGraph 把各节点组装成可执行的图。
    对应 docs/ARCHITECTURE.html sec-09 的节点链设计。

【何时被调用】
    - app/graph/chat_graph.py（非流式全图，测试与脚本使用）
    - app/graph/stream_state_preparer.py（SSE 流式路径的"前半段图"）

【图结构（含条件边）】
    load_skill → load_history → route_question
        ├─ needs_project / needs_web → retrieve_context → compact_history
        └─ 仅创作 → compact_history
    完整图继续：compact_history → generate → save_messages
    准备图到 compact_history 为止（SSE 流式时 generate 由服务层消费 Provider 流）。

【简例】
    graph = build_chat_graph(responder=None, repository=None, retrieval_pipeline=None)
    result = graph.invoke(initial_state)   # -> dict（AgentState 各字段）
"""

from langgraph.graph import END, START, StateGraph

from app.graph.graph_constants import (
    BRANCH_RETRIEVE,
    BRANCH_SKIP_RETRIEVE,
    NODE_COMPACT_HISTORY,
    NODE_GENERATE,
    NODE_LOAD_HISTORY,
    NODE_LOAD_SKILL,
    NODE_RETRIEVE_CONTEXT,
    NODE_ROUTE_QUESTION,
    NODE_SAVE_MESSAGES,
)
from app.graph.graph_node_adapters import (
    compact_history_adapter,
    load_skill_adapter,
    make_generate_adapter,
    make_load_history_adapter,
    make_retrieve_context_adapter,
    make_route_question_adapter,
    make_save_messages_adapter,
)
from app.graph.route_classifiers import RouteClassifiers
from app.graph.nodes.generate import Responder
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.schemas.agent_state import AgentState
from app.storage.postgres.conversation_repository import ConversationRepository


def should_retrieve(state: AgentState) -> str:
    """route_question 之后的条件边：判断是否进入检索节点。

    参数:
        state: 当前图状态（route 已写入）。

    返回:
        str: BRANCH_RETRIEVE（查库/联网）或 BRANCH_SKIP_RETRIEVE（仅创作）。
    """
    route = state.route
    if route is not None and (route.needs_project or route.needs_web):
        return BRANCH_RETRIEVE
    return BRANCH_SKIP_RETRIEVE


def _add_common_prefix_nodes(
    builder: StateGraph,
    repository: ConversationRepository | None,
    retrieval_pipeline: RetrievalPipeline | None,
    route_classifiers: RouteClassifiers | None,
) -> None:
    """向图注册公共前缀节点与条件边（skill → history → route →(条件)→ compact）。

    参数:
        builder: StateGraph 构建器。
        repository: 可选 PG Repository，绑定进 load_history。
        retrieval_pipeline: 可选检索流水线，绑定进 retrieve_context。
        route_classifiers: 可选路由级联分类器包。
    """
    builder.add_node(NODE_LOAD_SKILL, load_skill_adapter)
    builder.add_node(NODE_LOAD_HISTORY, make_load_history_adapter(repository))
    builder.add_node(NODE_ROUTE_QUESTION, make_route_question_adapter(route_classifiers))
    builder.add_node(NODE_RETRIEVE_CONTEXT, make_retrieve_context_adapter(retrieval_pipeline))
    builder.add_node(NODE_COMPACT_HISTORY, compact_history_adapter)
    builder.add_edge(START, NODE_LOAD_SKILL)
    builder.add_edge(NODE_LOAD_SKILL, NODE_LOAD_HISTORY)
    builder.add_edge(NODE_LOAD_HISTORY, NODE_ROUTE_QUESTION)
    builder.add_conditional_edges(
        NODE_ROUTE_QUESTION,
        should_retrieve,
        {
            BRANCH_RETRIEVE: NODE_RETRIEVE_CONTEXT,
            BRANCH_SKIP_RETRIEVE: NODE_COMPACT_HISTORY,
        },
    )
    builder.add_edge(NODE_RETRIEVE_CONTEXT, NODE_COMPACT_HISTORY)


def build_chat_graph(
    responder: Responder | None = None,
    repository: ConversationRepository | None = None,
    retrieval_pipeline: RetrievalPipeline | None = None,
    route_classifiers: RouteClassifiers | None = None,
):
    """组装完整 Chat 图（含 generate 与 save_messages）。

    参数:
        responder: 可选生成函数；测试注入用。
        repository: 可选 PG Repository。
        retrieval_pipeline: 可选检索流水线。
        route_classifiers: 可选路由级联分类器包。

    返回:
        CompiledStateGraph: 可 invoke 的 LangGraph 图。
    """
    builder = StateGraph(AgentState)
    _add_common_prefix_nodes(builder, repository, retrieval_pipeline, route_classifiers)
    builder.add_node(NODE_GENERATE, make_generate_adapter(responder))
    builder.add_node(NODE_SAVE_MESSAGES, make_save_messages_adapter(repository))
    builder.add_edge(NODE_COMPACT_HISTORY, NODE_GENERATE)
    builder.add_edge(NODE_GENERATE, NODE_SAVE_MESSAGES)
    builder.add_edge(NODE_SAVE_MESSAGES, END)
    return builder.compile()


def build_prepare_graph(
    repository: ConversationRepository | None = None,
    retrieval_pipeline: RetrievalPipeline | None = None,
    route_classifiers: RouteClassifiers | None = None,
):
    """组装 SSE 流式路径的"准备图"（到 compact_history 为止）。

    参数:
        repository: 可选 PG Repository。
        retrieval_pipeline: 可选检索流水线。
        route_classifiers: 可选路由级联分类器包。

    返回:
        CompiledStateGraph: 可 invoke 的 LangGraph 图。
    """
    builder = StateGraph(AgentState)
    _add_common_prefix_nodes(builder, repository, retrieval_pipeline, route_classifiers)
    builder.add_edge(NODE_COMPACT_HISTORY, END)
    return builder.compile()
