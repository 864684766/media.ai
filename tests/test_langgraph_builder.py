"""LangGraph 组图器测试。

【覆盖点】
    1. 完整图节点齐全，invoke 后 answer / message_ids 均有值。
    2. 准备图只执行到 compact_history，不触发 generate。
"""

from app.graph.graph_constants import (
    MEMORY_MESSAGE_ID_ASSISTANT,
    MEMORY_MESSAGE_ID_USER,
    NODE_COMPACT_HISTORY,
    NODE_GENERATE,
    NODE_LOAD_HISTORY,
    NODE_LOAD_SKILL,
    NODE_ROUTE_QUESTION,
    NODE_SAVE_MESSAGES,
)
from app.graph.graph_result_converter import to_agent_state
from app.graph.langgraph_builder import build_chat_graph, build_prepare_graph
from app.graph.state_factory import create_initial_state
from app.schemas.chat import ChatRequest


def _fake_responder(state) -> str:
    """测试用生成函数：不调用真实 Provider，返回固定回答。"""
    return f"echo: {state.question}"


def test_full_graph_contains_all_nodes() -> None:
    """完整图应包含设计文档 sec-09 规定的 6 个节点。"""
    graph = build_chat_graph(responder=_fake_responder)
    node_names = set(graph.get_graph().nodes.keys())
    expected = {
        NODE_LOAD_SKILL,
        NODE_LOAD_HISTORY,
        NODE_ROUTE_QUESTION,
        NODE_COMPACT_HISTORY,
        NODE_GENERATE,
        NODE_SAVE_MESSAGES,
    }
    assert expected.issubset(node_names)


def test_full_graph_invoke_produces_answer_and_message_ids() -> None:
    """完整图 invoke 后应有回答与消息 id（无 PG 时为 memory 占位）。"""
    graph = build_chat_graph(responder=_fake_responder)
    request = ChatRequest(message="你好")
    result = to_agent_state(graph.invoke(create_initial_state(request)))
    assert result.answer == "echo: 你好"
    assert result.message_ids == [MEMORY_MESSAGE_ID_USER, MEMORY_MESSAGE_ID_ASSISTANT]


def test_prepare_graph_stops_before_generate() -> None:
    """准备图应产出 prompt 与 route，但不生成 answer。"""
    graph = build_prepare_graph()
    request = ChatRequest(message="续写打斗")
    result = to_agent_state(graph.invoke(create_initial_state(request)))
    assert result.prompt != ""
    assert result.route is not None
    assert result.answer == ""
