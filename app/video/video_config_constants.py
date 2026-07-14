"""视频域配置键名（与 config/app.yaml video 段对应）。

【职责】
    避免在 video_config_reader 内联 YAML 键名字符串。
"""

YAML_KEY_VIDEO = "video"
YAML_KEY_STORYBOARD = "storyboard"
YAML_KEY_REPLACE_ON_SUBMIT = "replace_on_submit"
YAML_KEY_DEFAULT_STATUS = "default_status"
YAML_KEY_QA = "qa"
YAML_KEY_MAX_RETRIES = "max_retries"
YAML_KEY_COMPOSE = "compose"
YAML_KEY_OUTPUT_FILENAME = "output_filename"
YAML_KEY_REVIEW = "review"
YAML_KEY_REVIEW_STORYBOARD = "storyboard"
YAML_KEY_REVIEW_KEYFRAME = "keyframe"

# replace_on_submit 默认值：提交时全量替换同 project 镜头
DEFAULT_REPLACE_ON_SUBMIT = True
# QA 单镜最大自动重试次数（超限 → awaiting_review）
DEFAULT_QA_MAX_RETRIES = 3
# HITL 开关默认：V6 可先关闭，由 API 手动触发 review
DEFAULT_REVIEW_STORYBOARD_ENABLED = False
DEFAULT_REVIEW_KEYFRAME_ENABLED = True

# V7 compose 段额外键
YAML_KEY_OUTPUT_MP4_FILENAME = "output_mp4_filename"
