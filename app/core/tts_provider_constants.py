"""TTS Provider 名称常量（V8.5 一处权威）。"""

from app.core.audio_constants import DEFAULT_TTS_PROVIDER

# Provider 标识（与 app.yaml video.audio.tts_provider 对齐）
TTS_PROVIDER_STUB = DEFAULT_TTS_PROVIDER
TTS_PROVIDER_EDGE_TTS = "edge_tts"

# Edge TTS 默认音色（app.yaml 可覆盖）
DEFAULT_EDGE_VOICE = "zh-CN-XiaoxiaoNeural"

# YAML 键名
YAML_KEY_TTS_PROVIDER = "tts_provider"
YAML_KEY_EDGE_TTS = "edge_tts"
YAML_KEY_DEFAULT_VOICE = "default_voice"
YAML_KEY_COMPOSE_MUX = "mux_audio"
YAML_KEY_COMPOSE_BURN_SUBTITLES = "burn_subtitles"
YAML_KEY_VOICE_MAP = "voice_map"
YAML_KEY_BGM = "bgm"
YAML_KEY_BGM_DEFAULT_VOLUME = "default_volume"
