"""视频项目实体常量（V8+ 项目 CRUD 一处权威）。

【职责】
    video_projects 状态、默认画幅/预算等跨 API 与 ORM 引用的字面量。

【何时调用】
    创建项目、列表过滤、测试断言时 import。
"""

# 项目状态
PROJECT_STATUS_ACTIVE = "active"
PROJECT_STATUS_ARCHIVED = "archived"

# 默认技术规格
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_RESOLUTION = "1920x1080"
DEFAULT_PROJECT_FPS = 24
DEFAULT_TARGET_DURATION_SEC = 0.0

# project_id 合法字符（slug）
PROJECT_ID_MAX_LENGTH = 64
PROJECT_ID_PATTERN = r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$"

# 列表默认条数
DEFAULT_PROJECT_LIST_LIMIT = 50

# 项目描述最大字符数（选填，空串表示无描述）
MAX_PROJECT_DESCRIPTION_LENGTH = 500
