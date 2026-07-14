"""视频 Provider 域常量（V7 一处权威）。

【职责】
    Provider id、能力矩阵字段名、YAML 键名；编排与适配器共同引用。

【何时调用】
    video_provider_config_reader、clip/compose 分发器 import。

【简例】
    provider = VIDEO_PROVIDER_STUB  # → "stub"
"""

# Provider id：config video.providers.active 可选值
VIDEO_PROVIDER_STUB = "stub"
VIDEO_PROVIDER_LOCAL_FFMPEG = "local_ffmpeg"

# 合成 Provider 模式
COMPOSE_PROVIDER_STUB_JSON = "stub_json"
COMPOSE_PROVIDER_LOCAL_FFMPEG = "local_ffmpeg"

# 能力矩阵字段（app.yaml video.providers.matrix.<id>）
CAP_KEY_MAX_REF_IMAGES = "max_ref_images"
CAP_KEY_MAX_REF_VIDEOS = "max_ref_videos"
CAP_KEY_NATIVE_AUDIO = "native_audio"
CAP_KEY_MULTI_SHOT = "multi_shot"
CAP_KEY_COST_PER_SECOND = "cost_per_second"

# YAML 键
YAML_KEY_PROVIDERS = "providers"
YAML_KEY_ACTIVE = "active"
YAML_KEY_MATRIX = "matrix"
YAML_KEY_ACTIVE_KEYFRAME = "keyframe"
YAML_KEY_ACTIVE_CLIP = "clip"
YAML_KEY_ACTIVE_COMPOSE = "compose"

# 能力矩阵默认值
DEFAULT_MAX_REF_IMAGES = 1
DEFAULT_MAX_REF_VIDEOS = 0
DEFAULT_NATIVE_AUDIO = False
DEFAULT_MULTI_SHOT = False
DEFAULT_PROVIDER_COST_PER_SECOND = 0.0

# 默认 active Provider（与 V3 测试兼容）
DEFAULT_ACTIVE_KEYFRAME_PROVIDER = VIDEO_PROVIDER_STUB
DEFAULT_ACTIVE_CLIP_PROVIDER = VIDEO_PROVIDER_STUB
DEFAULT_ACTIVE_COMPOSE_PROVIDER = COMPOSE_PROVIDER_STUB_JSON
