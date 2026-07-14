"""应用启动配置（.env → AppSettings）。

【本文件职责】
    读取项目根 .env，提供 FastAPI **服务级** 配置：端口、调试、API 前缀、日志。

【与 config/app.yaml 的分工】（初学者必记）
    .env + 本文件 AppSettings  → 服务怎么「跑起来」
    config/app.yaml + config_resolver → Agent 怎么「干活」（检索条数、Profile 等）

【何时使用】
    app/run.py 启动 uvicorn 读 app_host、app_port
    app/api/* 拼路由前缀 settings.api_prefix

【示例】
    .env: APP_PORT=8000 → settings.app_port == 8000
    访问 chat: f"{settings.api_prefix}/chat" → /api/v1/chat
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core import constants


class AppSettings(BaseSettings):
    """应用全局配置（每项对应 .env 中的一个键，见 .env.example 中文说明）。

    参数说明:
        app_name: 应用名称，用于日志和文档展示。
        app_env: 运行环境，development 或 production。
        app_debug: 是否开启调试模式。
        app_host: 服务监听地址。
        app_port: 服务监听端口。
        api_prefix: API 路由统一前缀。
        log_level: 日志级别。
        database_url: PostgreSQL 连接串；空则 PG 存储层处于「未配置」。
        neo4j_uri: Neo4j Bolt 地址；空则 Neo4j 层处于「未配置」。
        neo4j_user: Neo4j 用户名。
        neo4j_password: Neo4j 密码。
        zhipu_api_key: 智谱 GLM API Key。
        deepseek_api_key: DeepSeek API Key。
        kimi_api_key: Kimi / Moonshot API Key。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = constants.DEFAULT_APP_NAME
    app_env: str = constants.DEFAULT_APP_ENV
    app_debug: bool = constants.DEFAULT_APP_DEBUG
    app_host: str = constants.DEFAULT_APP_HOST
    app_port: int = constants.DEFAULT_APP_PORT
    api_prefix: str = constants.DEFAULT_API_PREFIX
    log_level: str = constants.DEFAULT_LOG_LEVEL
    database_url: str | None = None
    neo4j_uri: str | None = None
    neo4j_user: str = constants.DEFAULT_NEO4J_USER
    neo4j_password: str | None = None
    zhipu_api_key: str | None = None
    deepseek_api_key: str | None = None
    kimi_api_key: str | None = None
    cors_origins: str = constants.DEFAULT_CORS_ORIGINS


# 全局单例：整个进程共享一份，from app.core.config import settings 即可
settings = AppSettings()
