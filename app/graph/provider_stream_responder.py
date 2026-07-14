"""Provider 流式生成适配层。

【职责】
    将 AgentState 交给当前 Provider，逐段产出 assistant 文本。
"""

from collections.abc import Iterable

from app.graph.provider_message_helper import build_missing_api_key_message
from app.graph.provider_request_builder import build_provider_request
from app.providers import build_current_provider
from app.providers.provider_settings_reader import load_model_config
from app.providers.provider_stream_models import ProviderStreamChunk
from app.schemas.agent_state import AgentState


def stream_provider_answer_chunks(state: AgentState) -> Iterable[str]:
    """调用当前 Provider 并逐段返回文本。

    参数:
        state: 当前图状态。

    返回:
        Iterable[str]: delta 文本片段。
    """
    model_config = load_model_config()
    if not model_config.api_key:
        yield build_missing_api_key_message(model_config.provider)
        return
    provider = build_current_provider()
    request = build_provider_request(state, stream=True)
    yield from provider.stream_chat(request)


def stream_provider_answer_events(state: AgentState) -> Iterable[ProviderStreamChunk]:
    """调用当前 Provider 并返回结构化流式事件。

    参数:
        state: 当前图状态。

    返回:
        Iterable[ProviderStreamChunk]: delta / usage 事件。
    """
    model_config = load_model_config()
    if not model_config.api_key:
        yield ProviderStreamChunk(delta=build_missing_api_key_message(model_config.provider))
        return
    provider = build_current_provider()
    request = build_provider_request(state, stream=True)
    yield from provider.stream_chat_chunks(request)
