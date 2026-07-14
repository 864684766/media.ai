"""CORS 中间件配置辅助。

【职责】
    从 .env 读取 CORS_ORIGINS，解析为允许的前端源列表。
    供 application.py 注册 CORSMiddleware 使用。
"""

from app.core import constants
from app.core.config import settings


def parse_cors_origins() -> list[str]:
    """解析 CORS 允许源列表。

    返回:
        list[str]: 去重后的 origin URL 列表。
    """
    raw = getattr(settings, "cors_origins", None)
    text = raw if isinstance(raw, str) and raw.strip() else constants.DEFAULT_CORS_ORIGINS
    return _split_origins(text)


def _split_origins(text: str) -> list[str]:
    """按逗号拆分并去空。"""
    parts = [item.strip() for item in text.split(",")]
    return [item for item in parts if item]
