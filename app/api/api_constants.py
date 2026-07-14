"""API 层路由前缀与路径常量。

【职责】
    集中管理各 API 模块的路由前缀，避免在路由文件中内联字符串。
"""

# 会话相关 API 前缀（完整路径：/api/v1/conversations）
CONVERSATIONS_ROUTE_PREFIX = "/conversations"

# Skill 列表 API 前缀（完整路径：/api/v1/skills）
SKILLS_ROUTE_PREFIX = "/skills"

# 会话列表默认条数（前端工作台左侧栏分页用）
DEFAULT_CONVERSATION_LIST_LIMIT = 50

# 知识库 API 前缀（完整路径：/api/v1/knowledge）
KNOWLEDGE_ROUTE_PREFIX = "/knowledge"

# 知识库文档列表默认条数
DEFAULT_KNOWLEDGE_LIST_LIMIT = 50

# 视频 API 前缀（完整路径：/api/v1/video）
VIDEO_ROUTE_PREFIX = "/video"

# 创作大纲 API 前缀（完整路径：/api/v1/creative）
CREATIVE_ROUTE_PREFIX = "/creative"

# 产物文件 API 前缀（/api/v1/files）
FILES_ROUTE_PREFIX = "/files"
