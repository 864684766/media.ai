"""Provider 错误分类。

【职责】
    将 httpx 的网络/HTTP 异常转成统一 ProviderCallError，便于 SSE error 展示。
"""

import httpx


class ProviderCallError(RuntimeError):
    """Provider 调用失败。

    参数说明:
        code: 错误分类，如 provider_http_error / provider_timeout。
        message: 人类可读说明。
    """

    def __init__(self, code: str, message: str) -> None:
        """初始化 Provider 错误。"""
        super().__init__(message)
        self.code = code
        self.message = message


def classify_provider_error(exc: Exception) -> ProviderCallError:
    """将外部调用异常分类为 ProviderCallError。

    参数:
        exc: 原始异常。

    返回:
        ProviderCallError: 统一错误。
    """
    if isinstance(exc, ProviderCallError):
        return exc
    if isinstance(exc, httpx.TimeoutException):
        return ProviderCallError("provider_timeout", f"Provider 调用超时：{exc}")
    if isinstance(exc, httpx.HTTPStatusError):
        return _from_http_status_error(exc)
    if isinstance(exc, httpx.RequestError):
        return ProviderCallError("provider_network_error", f"Provider 网络错误：{exc}")
    return ProviderCallError("provider_unknown_error", f"Provider 未知错误：{exc}")


def _from_http_status_error(exc: httpx.HTTPStatusError) -> ProviderCallError:
    """根据 HTTP 状态码构造错误。"""
    status_code = exc.response.status_code
    code = "provider_auth_error" if status_code in (401, 403) else "provider_http_error"
    return ProviderCallError(code, f"Provider HTTP {status_code}：{exc.response.text}")
