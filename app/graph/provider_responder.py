"""Provider 生成器适配层。

【职责】
    将 AgentState 转为 Provider 请求，并返回 assistant 文本。

【为什么单独放】
    generate 节点只负责「写 state.answer」，具体怎么调用模型放在这里，
    后续改流式、换 Provider、加错误处理时不污染节点文件。
"""

from app.graph.provider_request_builder import build_provider_request
from app.graph.provider_message_helper import build_missing_api_key_message
from app.providers import build_current_provider
from app.providers.provider_settings_reader import load_model_config
from app.schemas.agent_state import AgentState


def build_provider_answer(state: AgentState) -> str:
    """调用当前 Provider 生成答案。

    参数:
        state: 当前图状态，至少包含 prompt/question/skill。

    返回:
        str: assistant 回复；无 API Key 时返回可读提示。
    """
    model_config = load_model_config()
    if not model_config.api_key:
        return build_missing_api_key_message(model_config.provider)
    provider = build_current_provider()
    result = provider.chat(build_provider_request(state, stream=False))
    return result.content

