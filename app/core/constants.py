"""应用配置常量。

集中维护所有字面量形式的配置键名与默认值，避免在代码中散落硬编码。
"""

# 环境变量键名
ENV_KEY_APP_NAME = "APP_NAME"
ENV_KEY_APP_ENV = "APP_ENV"
ENV_KEY_APP_DEBUG = "APP_DEBUG"
ENV_KEY_APP_HOST = "APP_HOST"
ENV_KEY_APP_PORT = "APP_PORT"
ENV_KEY_APP_API_PREFIX = "APP_API_PREFIX"
ENV_KEY_LOG_LEVEL = "LOG_LEVEL"

# 默认值
DEFAULT_APP_NAME = "lanmo"
DEFAULT_APP_ENV = "development"
DEFAULT_APP_DEBUG = True
DEFAULT_APP_HOST = "0.0.0.0"
DEFAULT_APP_PORT = 8000
DEFAULT_API_PREFIX = "/api/v1"
DEFAULT_LOG_LEVEL = "INFO"

# 运行环境取值
ENV_VALUE_PRODUCTION = "production"
ENV_VALUE_DEVELOPMENT = "development"

# ASGI 应用加载路径（模块:变量名）
ASGI_APP_PATH = "app.application:app"

# Chat 接口常量
CHAT_ROUTE_PREFIX = "/chat"
DEFAULT_CHAT_REPLY = "hello from chat"

# 路由自动扫描常量
API_PACKAGE_NAME = "app.api"
ROUTER_ATTR_NAME = "router"
EXCLUDED_API_MODULES = frozenset({"router", "router_loader", "deps"})
