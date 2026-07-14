"""LangGraph 执行结果转换器。

【职责】
    LangGraph 的 invoke() 返回的是「字段名 -> 值」的 dict，
    本模块把它还原成项目内统一使用的 AgentState，方便下游按属性访问。

【简例】
    result = graph.invoke(initial_state)     # dict
    state = to_agent_state(result)           # AgentState
"""

from app.schemas.agent_state import AgentState


def to_agent_state(result: dict | AgentState) -> AgentState:
    """把图执行结果统一转换为 AgentState。

    参数:
        result: graph.invoke() 的返回值；dict 或已是 AgentState。

    返回:
        AgentState: 统一后的状态对象。
    """
    if isinstance(result, AgentState):
        return result
    return AgentState.model_validate(result)
