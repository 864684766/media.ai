"""策划→分镜 LLM 非流式调用。"""

from app.core.constants import ROLE_SYSTEM, ROLE_USER
from app.providers import ChatCompletionRequest, ChatMessage, build_current_provider
from app.providers.provider_settings_reader import load_model_config


def run_plan_storyboard_llm(user_prompt: str, system_prompt: str) -> str:
    """调用当前 Provider 生成分镜 JSON 文本。

    参数:
        user_prompt: 用户消息（含已确认大纲）。
        system_prompt: storyboard Skill system prompt。

    返回:
        str: assistant 全文；无 API Key 时返回空串以触发模板 fallback。
    """
    model_config = load_model_config()
    if not model_config.api_key:
        return ""
    provider = build_current_provider()
    request = _build_request(user_prompt, system_prompt)
    result = provider.chat(request)
    return result.content or ""


def _build_request(user_prompt: str, system_prompt: str) -> ChatCompletionRequest:
    """构造非流式 ChatCompletionRequest。"""
    messages: list[ChatMessage] = []
    if system_prompt.strip():
        messages.append(ChatMessage(role=ROLE_SYSTEM, content=system_prompt))
    messages.append(ChatMessage(role=ROLE_USER, content=user_prompt))
    return ChatCompletionRequest(messages=messages, stream=False)
