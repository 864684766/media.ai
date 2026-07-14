"""对话图模块。

【职责】
    组织 load_skill / load_history / route / compact / generate / save 等节点，
    并用真实 LangGraph StateGraph 组图（见 langgraph_builder.py）。

【当前阶段】
    已接入 langgraph.StateGraph；节点实现仍是纯函数（app/graph/nodes/），
    通过 graph_node_adapters.py 适配为 LangGraph 节点签名。
"""

from app.graph.chat_graph import run_minimal_chat_graph

__all__ = ["run_minimal_chat_graph"]
