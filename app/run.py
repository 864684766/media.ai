"""服务器启动入口。

封装 uvicorn 启动参数，日常开发通过 `python -m app.run` 运行。
"""

import uvicorn

from app.core.config import settings
from app.core.constants import ASGI_APP_PATH, ENV_VALUE_DEVELOPMENT


def _build_run_kwargs() -> dict:
    """构造 uvicorn 启动参数。

    返回:
        dict: uvicorn.run 所需的关键字参数。
    """
    kwargs = {
        "host": settings.app_host,
        "port": settings.app_port,
        "log_level": settings.log_level.lower(),
    }
    if settings.app_env == ENV_VALUE_DEVELOPMENT:
        kwargs["reload"] = True
    return kwargs


def run() -> None:
    """启动 uvicorn 服务。"""
    uvicorn.run(ASGI_APP_PATH, **_build_run_kwargs())


if __name__ == "__main__":
    run()
