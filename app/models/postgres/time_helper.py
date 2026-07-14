"""PostgreSQL ORM 时间辅助方法。

【职责】
    统一生成 UTC 时间，供多个 ORM 模型复用。
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """返回 UTC 当前时间。

    返回:
        datetime: 带 UTC 时区的当前时间。
    """
    return datetime.now(timezone.utc)
