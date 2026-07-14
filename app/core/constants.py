"""应用配置常量。

集中维护所有字面量形式的配置键名与默认值，避免在代码中散落硬编码。

【字面量治理原则（约定大于配置）】
    约定本身必须有唯一权威定义处：跨层共用的字面量放本文件，
    某一层内部的字面量放该层 *_constants.py，其余位置一律 import 引用。
    详见 docs/ARCHITECTURE.html sec-08「约定大于配置与字面量治理」。
"""

# 环境变量键名
ENV_KEY_APP_NAME = "APP_NAME"
ENV_KEY_APP_ENV = "APP_ENV"
ENV_KEY_APP_DEBUG = "APP_DEBUG"
ENV_KEY_APP_HOST = "APP_HOST"
ENV_KEY_APP_PORT = "APP_PORT"
ENV_KEY_APP_API_PREFIX = "APP_API_PREFIX"
ENV_KEY_LOG_LEVEL = "LOG_LEVEL"
ENV_KEY_DATABASE_URL = "DATABASE_URL"
ENV_KEY_NEO4J_URI = "NEO4J_URI"
ENV_KEY_NEO4J_USER = "NEO4J_USER"
ENV_KEY_NEO4J_PASSWORD = "NEO4J_PASSWORD"
ENV_KEY_ZHIPU_API_KEY = "ZHIPU_API_KEY"
ENV_KEY_DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"
ENV_KEY_KIMI_API_KEY = "KIMI_API_KEY"

# 默认值
DEFAULT_APP_NAME = "lanmo"
DEFAULT_APP_ENV = "development"
DEFAULT_APP_DEBUG = True
DEFAULT_APP_HOST = "0.0.0.0"
DEFAULT_APP_PORT = 8000
DEFAULT_API_PREFIX = "/api/v1"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_NEO4J_USER = "neo4j"
DEFAULT_PG_HEALTH_SQL = "SELECT 1"
DEFAULT_NEO4J_HEALTH_CYPHER = "RETURN 1 AS ok"

# 运行环境取值
ENV_VALUE_PRODUCTION = "production"
ENV_VALUE_DEVELOPMENT = "development"

# ASGI 应用加载路径（模块:变量名）
ASGI_APP_PATH = "app.application:app"

# 对话消息角色（唯一权威定义处；OpenAI 协议与 PG messages.role 共用同一套取值）
# providers / storage / graph 各层一律引用这里，不得重复定义或内联
ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"

# RouteDecision.domain 取值（sec-15 跨层契约：schemas 定义模型、graph 写入取值）
ROUTE_DOMAIN_GENERAL = "general"
ROUTE_DOMAIN_PROJECT = "project"
ROUTE_DOMAIN_REALTIME = "realtime"
ROUTE_DOMAIN_COMPOSITE = "composite"

# RouteDecision.reason 的模型默认值（未经过路由节点时的占位说明）
ROUTE_REASON_DEFAULT = "默认创作通道（未经过路由节点）"

# Chat 接口常量
CHAT_ROUTE_PREFIX = "/chat"
SSE_MEDIA_TYPE = "text/event-stream"
SSE_EVENT_MESSAGE_START = "message_start"
SSE_EVENT_CONTENT_DELTA = "content_delta"
SSE_EVENT_MESSAGE_END = "message_end"
SSE_EVENT_ERROR = "error"
SSE_EVENT_USAGE = "usage"
SSE_EVENT_CITATION = "citation"
SSE_EVENT_STATUS = "status"
SSE_EVENT_CLARIFICATION_REQUEST = "clarification_request"
SSE_EVENT_REQUIREMENTS_SUMMARY = "requirements_summary"
SSE_EVENT_CLARIFICATION_COMPLETE = "clarification_complete"
SSE_EVENT_OUTLINE_PROPOSED = "outline_proposed"
SSE_EVENT_OUTLINE_REVISED = "outline_revised"
SSE_EVENT_OUTLINE_APPROVED = "outline_approved"
DEFAULT_SSE_ERROR_CODE = "chat_error"

# SSE status 事件 phase 取值（准备图 / 生成阶段）
STATUS_PHASE_THINKING = "thinking"
STATUS_PHASE_GENERATING = "generating"

# SSE 事件 data 字段键名（sec-15 对外契约；客户端按这些键解析，不得内联散写）
SSE_FIELD_CONVERSATION_ID = "conversation_id"
SSE_FIELD_MESSAGE_IDS = "message_ids"
SSE_FIELD_DELTA = "delta"
SSE_FIELD_ERROR_CODE = "code"
SSE_FIELD_ERROR_MESSAGE = "message"
SSE_FIELD_CITATION_CHUNK_ID = "chunk_id"
SSE_FIELD_CITATION_SOURCE = "source"
SSE_FIELD_CITATION_EXCERPT = "excerpt"
SSE_FIELD_STATUS_PHASE = "phase"
SSE_FIELD_CLARIFICATION_SESSION_ID = "session_id"
SSE_FIELD_CLARIFICATION_ROUND = "round"
SSE_FIELD_CLARIFICATION_QUESTIONS = "questions"
SSE_FIELD_REQUIREMENTS_SUMMARY = "summary_md"
SSE_FIELD_ANSWERS_SNAPSHOT = "answers_snapshot"
SSE_FIELD_PLAN_ID = "plan_id"
SSE_FIELD_PLAN_VERSION = "version"
SSE_FIELD_PLAN_TITLE = "title"
SSE_FIELD_PLAN_CONTENT_MD = "content_md"
SSE_FIELD_PLAN_CREATION_TYPE = "creation_type"
SSE_FIELD_PLAN_APPROVED_AT = "approved_at"

# 路由自动扫描常量
API_PACKAGE_NAME = "app.api"
ROUTER_ATTR_NAME = "router"
EXCLUDED_API_MODULES = frozenset({"router", "router_loader", "deps"})

# CORS：允许前端 dev 源（.env CORS_ORIGINS 逗号分隔，默认 Vite 5173）
DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
ENV_KEY_CORS_ORIGINS = "CORS_ORIGINS"
CORS_ALLOW_METHODS = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
CORS_ALLOW_HEADERS = "Content-Type,Authorization"
