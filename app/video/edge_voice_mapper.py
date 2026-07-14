"""voice_id → Edge TTS 音色映射。"""

from app.core.tts_provider_constants import DEFAULT_EDGE_VOICE


def resolve_edge_voice(
    voice_id: str,
    default_voice: str,
    voice_map: dict[str, str] | None = None,
) -> str:
    """将 character_bible.voice_id 解析为 Edge 音色名。

    参数:
        voice_id: 角色配置的 voice_id。
        default_voice: app.yaml 默认音色。
        voice_map: app.yaml voice_map 覆盖表。

    返回:
        str: Edge TTS voice 名称。
    """
    text = (voice_id or "").strip()
    mapping = voice_map or {}
    if text and text in mapping:
        return mapping[text]
    if _looks_like_edge_voice(text):
        return text
    return default_voice or DEFAULT_EDGE_VOICE


def _looks_like_edge_voice(value: str) -> bool:
    """是否已是 Edge 音色格式（如 zh-CN-XiaoxiaoNeural）。"""
    return "-" in value and len(value) > 8
