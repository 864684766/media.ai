"""BGM 域常量（V8.6 一处权威）。"""

# 落盘目录段（相对 project）
BGM_STORAGE_SEGMENT = "audio/bgm"

# 上传允许的扩展名（小写）
BGM_ALLOWED_EXTENSIONS = (".mp3", ".wav", ".m4a", ".aac")

# 默认 BGM 混音音量（0.0–1.0，app.yaml 可覆盖）
DEFAULT_BGM_VOLUME = 0.25

# YAML 键
YAML_KEY_BGM_BLOCK = "bgm"
YAML_KEY_BGM_DEFAULT_VOLUME = "default_volume"
YAML_KEY_BGM_PAUSE_BEFORE_COMPOSE = "pause_before_compose"

# 合成前是否暂停等待用户上传 BGM（默认 true）
DEFAULT_BGM_PAUSE_BEFORE_COMPOSE = True
