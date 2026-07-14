"""视频预算域常量（V7）。

【职责】
    budget 配置键名与默认值；熔断原因与 compose mp4 文件名。

【何时调用】
    video_budget_config_reader、project_budget_gate import。
"""

# YAML 键（video.budget 段）
YAML_KEY_BUDGET = "budget"
YAML_KEY_DEFAULT_LIMIT_USD = "default_limit_usd"
YAML_KEY_FUSE_ON_RENDER = "fuse_on_render"
YAML_KEY_FUSE_ON_COMPOSE = "fuse_on_compose"
YAML_KEY_OUTPUT_MP4_FILENAME = "output_mp4_filename"

# 预算默认：0 表示不限额
DEFAULT_BUDGET_LIMIT_USD = 0.0
DEFAULT_FUSE_ON_RENDER = True
DEFAULT_FUSE_ON_COMPOSE = True

# V7 ffmpeg 合成默认成片文件名
DEFAULT_COMPOSE_MP4_FILENAME = "timeline.mp4"

# 熔断 HTTP/API 原因码
REASON_BUDGET_EXCEEDED = "budget_exceeded"
