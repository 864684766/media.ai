"""Provider 消息辅助。

【职责】
    统一生成 Provider 相关的人类可读提示。
"""


def build_missing_api_key_message(provider_id: str) -> str:
    """返回缺少 API Key 时的友好提示。

    参数:
        provider_id: 当前 provider id。

    返回:
        str: 提示文本。
    """
    return f"当前 Provider({provider_id}) 未配置 API Key，请在 .env 中补充后再调用真实模型。"
