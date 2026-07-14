"""route_question 节点。

【职责】
    调用路由级联（L1 规则 → L2 语义 → L3 LLM）推断能力开关，写入 state.route。
"""

from app.graph.route_cascade import decide_route
from app.graph.route_classifiers import RouteClassifiers
from app.schemas.agent_state import AgentState


def route_question_node(
    state: AgentState,
    classifiers: RouteClassifiers | None = None,
) -> AgentState:
    """通过级联推断并写入 RouteDecision。

    参数:
        state: 当前图状态。
        classifiers: 可选 L2/L3 分类器包。

    返回:
        AgentState: 写入 route 后的新状态。
    """
    route = decide_route(state.question, classifiers=classifiers)
    return state.model_copy(update={"route": route})
