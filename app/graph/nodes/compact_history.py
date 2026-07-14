"""compact_history 节点。

【职责】
    将 Skill、history、用户问题拼装成 state.prompt。
"""

from app.graph.history_compactor import compact_history_if_needed
from app.graph.prompt_builder import build_prompt_text
from app.schemas.agent_state import AgentState


def compact_history_node(state: AgentState) -> AgentState:
    """构造 prompt 骨架；必要时压缩历史。

    参数:
        state: 当前图状态。

    返回:
        AgentState: 写入 prompt 后的新状态。
    """
    compacted = compact_history_if_needed(state)
    prompt = build_prompt_text(compacted)
    return compacted.model_copy(update={"prompt": prompt})
