"""load_skill 节点。

【职责】
    从 app/skills Registry 加载当前 Skill，并写入 state.skill。
"""

from app.schemas.agent_state import AgentState
from app.skills import load_skill_context


def load_skill_node(state: AgentState, skill_id: str | None = None) -> AgentState:
    """加载 SkillContext。

    参数:
        state: 当前图状态。
        skill_id: 请求指定的 Skill id。

    返回:
        AgentState: 写入 skill 后的新状态。
    """
    skill = load_skill_context(
        skill_id=skill_id,
        user_message=state.question,
        creation_type=state.creation_type,
    )
    return state.model_copy(update={"skill": skill})
