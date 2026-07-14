"""大纲闸门判定（阶段 G · L0 策划闸门）。

【职责】
    对标成熟产品「先 Plan 后 Generate」：未确认大纲时拦截长篇创作输出。

【何时调用】
    outline_gate_stream_service 在 Provider 生成前。
"""

from app.core.clarification_constants import CREATION_TYPE_NOVEL, CREATION_TYPE_VIDEO
from app.core.creative_config_reader import OutlineConfig
from app.core.outline_gate_constants import OUTLINE_GATE_EXEMPT_KEYWORDS
from app.schemas.agent_state import AgentState
from app.schemas.chat import ChatRequest


def should_enforce_outline_gate(request: ChatRequest, state: AgentState, cfg: OutlineConfig) -> bool:
    """是否启用大纲闸门检查。

    参数:
        request: Chat 请求。
        state: 已准备完成的 AgentState。
        cfg: 大纲配置。

    返回:
        bool: True 表示须检查 approved 大纲。
    """
    if not cfg.enabled:
        return False
    if request.clarification_response is not None:
        return False
    if request.creation_type not in (CREATION_TYPE_NOVEL, CREATION_TYPE_VIDEO):
        return False
    if _is_exempt_message(request.message):
        return False
    return _is_creative_route(state)


def _is_exempt_message(message: str) -> bool:
    """设定查询 / 局部润色类消息豁免闸门。"""
    text = message.strip()
    if not text:
        return True
    return any(word in text for word in OUTLINE_GATE_EXEMPT_KEYWORDS)


def _is_creative_route(state: AgentState) -> bool:
    """路由是否走创作通道（非纯检索）。"""
    if state.route is None:
        return True
    if state.route.needs_project and not state.route.needs_creative:
        return False
    return bool(state.route.needs_creative)
