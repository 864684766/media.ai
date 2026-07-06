"""应用配置定义。

通过 pydantic-settings 从环境变量加载配置，统一对外暴露 `settings` 实例。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core import constants


class AppSettings(BaseSettings):
    """应用全局配置。

    参数说明:
        app_name: 应用名称，用于日志和文档展示。
        app_env: 运行环境，development 或 production。
        app_debug: 是否开启调试模式。
        app_host: 服务监听地址。
        app_port: 服务监听端口。
        api_prefix: API 路由统一前缀。
        log_level: 日志级别。
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


# 全局单例配置
settings = AppSettings()
