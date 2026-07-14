"""PostgreSQL 存储层常量。

【字面量治理】
    消息角色的权威定义在 app/core/constants.py（跨层共用）；
    本文件仅保留存储层别名引用，不重复定义字符串。
"""

from app.core import constants as core_constants

# SQLAlchemy 连接池参数（L1 常量，后续可抽到 config_constants）
PG_POOL_SIZE = 5
PG_MAX_OVERFLOW = 10
PG_POOL_PRE_PING = True
PG_POOL_RECYCLE_SEC = 1800

# 健康检查 SQL
PG_HEALTH_SQL = "SELECT 1"

# 表名与外键（ORM 与 Repository 统一引用）
TABLE_CONVERSATIONS = "conversations"
TABLE_MESSAGES = "messages"
TABLE_DOCUMENTS = "documents"
TABLE_CHUNKS = "chunks"
TABLE_SHOTS = "shots"
TABLE_CHARACTER_BIBLE = "character_bible"
TABLE_SCENE_LOCK = "scene_lock"
TABLE_PROP_INVENTORY = "prop_inventory"
TABLE_VIDEO_RENDER_JOBS = "video_render_jobs"
TABLE_SHOT_ASSETS = "shot_assets"
TABLE_COMPOSE_JOBS = "compose_jobs"
TABLE_VIDEO_PROJECTS = "video_projects"
TABLE_AUDIO_ASSETS = "audio_assets"
TABLE_CLARIFICATION_SESSIONS = "clarification_sessions"
TABLE_CREATIVE_PLANS = "creative_plans"
TABLE_VIDEO_PIPELINE_JOBS = "video_pipeline_jobs"

# 默认视频资产根目录
DEFAULT_VIDEO_ASSETS_DIR = "data/video_assets"
CONVERSATION_ID_COLUMN = "conversations.id"
CONVERSATION_FK = CONVERSATION_ID_COLUMN
DOCUMENT_ID_COLUMN = "documents.id"
DOCUMENT_FK = DOCUMENT_ID_COLUMN

# 消息角色（引用 core 权威定义，保持存储层原有命名以免大面积改动）
MESSAGE_ROLE_USER = core_constants.ROLE_USER
MESSAGE_ROLE_ASSISTANT = core_constants.ROLE_ASSISTANT
MESSAGE_ROLE_SYSTEM = core_constants.ROLE_SYSTEM
