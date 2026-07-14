"""执行 Alembic 升级到 head。

【运行】
    poetry run python scripts/run_alembic_upgrade.py

【说明】
    等价于 poetry run alembic upgrade head；未配置 DATABASE_URL 时退出。
"""

import subprocess
import sys

from app.storage.postgres.postgres_settings_reader import is_postgres_configured


def main() -> None:
    """调用 alembic upgrade head。"""
    if not is_postgres_configured():
        print("未配置 DATABASE_URL，无法执行迁移。")
        sys.exit(1)
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=False,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
