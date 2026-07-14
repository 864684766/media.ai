"""video.audio 配置读取（TTS / compose mux / BGM）。"""

from dataclasses import dataclass

from app.core.bgm_constants import (
    DEFAULT_BGM_VOLUME,
    DEFAULT_BGM_PAUSE_BEFORE_COMPOSE,
    YAML_KEY_BGM_DEFAULT_VOLUME,
    YAML_KEY_BGM_PAUSE_BEFORE_COMPOSE,
)
from app.core.config_yaml_loader import load_app_yaml
from app.core.tts_provider_constants import (
    DEFAULT_EDGE_VOICE,
    DEFAULT_TTS_PROVIDER,
    TTS_PROVIDER_EDGE_TTS,
    TTS_PROVIDER_STUB,
    YAML_KEY_BGM,
    YAML_KEY_COMPOSE_BURN_SUBTITLES,
    YAML_KEY_COMPOSE_MUX,
    YAML_KEY_DEFAULT_VOICE,
    YAML_KEY_EDGE_TTS,
    YAML_KEY_TTS_PROVIDER,
    YAML_KEY_VOICE_MAP,
)


@dataclass(frozen=True)
class VideoAudioConfig:
    """视频音频配置。"""

    tts_provider: str
    edge_default_voice: str
    voice_map: dict[str, str]
    bgm_default_volume: float
    bgm_pause_before_compose: bool
    compose_mux_audio: bool
    compose_burn_subtitles: bool


def load_video_audio_config() -> VideoAudioConfig:
    """从 app.yaml 读取 video.audio。"""
    root = load_app_yaml()
    video = root.get("video", {}) if isinstance(root, dict) else {}
    block = video.get("audio", {}) if isinstance(video, dict) else {}
    edge = block.get(YAML_KEY_EDGE_TTS, {}) if isinstance(block, dict) else {}
    compose = block.get("compose", {}) if isinstance(block, dict) else {}
    bgm = block.get(YAML_KEY_BGM, {}) if isinstance(block, dict) else {}
    provider = str(block.get(YAML_KEY_TTS_PROVIDER, DEFAULT_TTS_PROVIDER))
    return VideoAudioConfig(
        tts_provider=_normalize_provider(provider),
        edge_default_voice=str(edge.get(YAML_KEY_DEFAULT_VOICE, DEFAULT_EDGE_VOICE)),
        voice_map=_parse_voice_map(edge.get(YAML_KEY_VOICE_MAP, {})),
        bgm_default_volume=float(bgm.get(YAML_KEY_BGM_DEFAULT_VOLUME, DEFAULT_BGM_VOLUME)),
        bgm_pause_before_compose=bool(
            bgm.get(YAML_KEY_BGM_PAUSE_BEFORE_COMPOSE, DEFAULT_BGM_PAUSE_BEFORE_COMPOSE),
        ),
        compose_mux_audio=bool(compose.get(YAML_KEY_COMPOSE_MUX, True)),
        compose_burn_subtitles=bool(compose.get(YAML_KEY_COMPOSE_BURN_SUBTITLES, True)),
    )


def _normalize_provider(raw: str) -> str:
    """校验 provider 取值。"""
    if raw == TTS_PROVIDER_EDGE_TTS:
        return TTS_PROVIDER_EDGE_TTS
    return TTS_PROVIDER_STUB


def _parse_voice_map(raw: object) -> dict[str, str]:
    """解析 voice_map 为 str→str。"""
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items() if str(k).strip() and str(v).strip()}
