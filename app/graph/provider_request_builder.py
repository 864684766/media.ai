"""Provider 请求构造器。

【职责】
    将 AgentState 转成 ChatCompletionRequest，供非流式和流式 Provider 复用。
"""

from app.core.constants import ROLE_SYSTEM, ROLE_USER
from app.providers import ChatCompletionRequest, ChatMessage
from app.schemas.agent_state import AgentState


def build_provider_request(
    state: AgentState,
    stream: bool,
) -> ChatCompletionRequest:
    """把 AgentState 转成 Provider 请求。

    参数:
        state: 当前图状态。
        stream: 是否流式。

    返回:
        ChatCompletionRequest: Provider 可直接使用的请求模型。
    """
    return ChatCompletionRequest(messages=_build_messages(state), stream=stream)


def _build_messages(state: AgentState) -> list[ChatMessage]:
    """构造 Chat Completions messages。"""
    messages: list[ChatMessage] = []
    if state.skill is not None and state.skill.system_prompt:
        messages.append(ChatMessage(role=ROLE_SYSTEM, content=state.skill.system_prompt))
    messages.append(ChatMessage(role=ROLE_USER, content=state.prompt or state.question))
    return messages
