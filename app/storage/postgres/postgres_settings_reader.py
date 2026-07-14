"""PostgreSQL 连接配置读取。

从 AppSettings 读取 DATABASE_URL，判断 PG 是否已配置。
"""

from app.core.config import settings


def is_postgres_configured() -> bool:
    """判断 .env 是否提供了可用的 DATABASE_URL。

    返回:
        bool: 非空字符串时为 True。
    """
    url = settings.database_url
    return isinstance(url, str) and bool(url.strip())


def get_postgres_url() -> str | None:
    """读取 PostgreSQL 连接串。

    返回:
        str | None: 已配置则返回 URL，否则 None。
    """
    if not is_postgres_configured():
        return None
    return settings.database_url.strip()
