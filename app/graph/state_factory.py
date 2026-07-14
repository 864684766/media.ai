"""AgentState 创建器。

【职责】
    将 ChatRequest 转换为图内初始 AgentState。
"""

from uuid import uuid4

from app.core.config_resolver import resolve
from app.schemas.agent_state import AgentState
from app.schemas.chat import ChatRequest
from app.services.clarification_summary_builder import format_clarification_user_message


def create_initial_state(request: ChatRequest) -> AgentState:
    """根据 ChatRequest 创建初始 state。

    参数:
        request: HTTP 请求体。

    返回:
        AgentState: 图执行的初始状态。
    """
    conversation_id = request.conversation_id or str(uuid4())
    question = _resolve_question(request)
    return AgentState(
        question=question,
        conversation_id=conversation_id,
        thread_id=conversation_id,
        project_id=request.project_id,
        requested_skill_id=request.skill_id,
        creation_type=request.creation_type,
        runtime_config=resolve(),
    )


def _resolve_question(request: ChatRequest) -> str:
    """解析本轮写入 state 的用户文本。"""
    if request.clarification_response is not None:
        return format_clarification_user_message(request.clarification_response.answers)
    return request.message
