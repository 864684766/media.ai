"""Provider 连通性检查。

【职责】
    用一个极短请求验证当前 LLM Provider 是否可用。

【安全说明】
    返回结果不会打印 API Key；真实调用只在用户主动运行脚本时发生。
"""

from app.providers import provider_constants as pc
from app.providers.provider_models import (
    ChatCompletionRequest,
    ChatMessage,
    ProviderHealthResult,
)
from app.providers.provider_settings_reader import load_model_config
from app.providers.registry import build_current_provider


def check_provider_health() -> ProviderHealthResult:
    """检查当前 Provider 是否配置并可达。

    返回:
        ProviderHealthResult: Provider 健康检查结果。
    """
    config = load_model_config()
    if not config.api_key:
        return _not_configured_result(config.provider, config.model)
    return _probe_provider(config.provider, config.model)


def _not_configured_result(provider: str, model: str) -> ProviderHealthResult:
    """未配置 API Key 时的结果。"""
    return ProviderHealthResult(
        provider=provider,
        model=model,
        configured=False,
        reachable=False,
        message="未配置 API Key，跳过真实模型调用",
    )


def _probe_provider(provider: str, model: str) -> ProviderHealthResult:
    """向当前 Provider 发送极短请求。"""
    try:
        llm_provider = build_current_provider()
        result = llm_provider.chat(_build_health_request())
        return _reachable_result(provider, model, result.content)
    except Exception as exc:  # noqa: BLE001 — 健康检查需捕获所有外部调用错误
        return _failed_result(provider, model, exc)


def _build_health_request() -> ChatCompletionRequest:
    """构造健康检查请求。"""
    return ChatCompletionRequest(
        messages=[ChatMessage(role="user", content=pc.PROVIDER_HEALTH_CHECK_PROMPT)],
        temperature=0.0,
    )


def _reachable_result(
    provider: str,
    model: str,
    content: str,
) -> ProviderHealthResult:
    """Provider 成功响应时的结果。"""
    preview = content.strip()[:30]
    return ProviderHealthResult(
        provider=provider,
        model=model,
        configured=True,
        reachable=True,
        message=f"Provider 调用正常，响应预览：{preview}",
    )


def _failed_result(
    provider: str,
    model: str,
    exc: Exception,
) -> ProviderHealthResult:
    """Provider 调用失败时的结果。"""
    return ProviderHealthResult(
        provider=provider,
        model=model,
        configured=True,
        reachable=False,
        message=f"Provider 调用失败：{exc}",
    )
