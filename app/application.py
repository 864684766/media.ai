"""FastAPI 应用定义。

负责构建 FastAPI 实例并注册路由；启动服务请使用 `app/run.py`。
"""

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import logger
from app.utils.meta import get_app_version


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。

    返回:
        FastAPI: 已注册路由和中间件的应用实例。
    """
    application = FastAPI(
        title=settings.app_name,
        version=get_app_version(),
        debug=settings.app_debug,
    )
    application.include_router(api_router, prefix=settings.api_prefix)
    logger.info("应用实例已创建: %s", settings.app_name)
    return application


app = create_app()
