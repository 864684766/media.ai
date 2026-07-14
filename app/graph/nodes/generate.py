"""generate 节点。

【职责】
    生成 assistant 回复，并写入 state.answer。

【默认行为】
    未注入 responder 时，尝试通过 Provider Registry 调用真实模型；
    若未配置 API Key，则返回清晰提示而不是让接口崩溃。
"""

from collections.abc import Callable

from app.graph.provider_responder import build_provider_answer
from app.schemas.agent_state import AgentState

Responder = Callable[[AgentState], str]


def generate_node(state: AgentState, responder: Responder | None = None) -> AgentState:
    """生成 assistant 回复。

    参数:
        state: 当前图状态。
        responder: 可选生成函数；测试或未来 Provider 接入时注入。

    返回:
        AgentState: 写入 answer 后的新状态。
    """
    answer = responder(state) if responder is not None else build_provider_answer(state)
    return state.model_copy(update={"answer": answer})
