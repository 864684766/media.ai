"""PostgreSQL 建表脚本（学习/快速验证版）。

【用途】
    根据当前 ORM 模型创建全部表。

【运行】
    推荐：poetry run python scripts/run_alembic_upgrade.py
    或：  poetry run python scripts/init_postgres_tables.py（测试/本地快捷）

【边界】
    生产与协作环境请使用 Alembic 增量迁移。
"""

from app.storage.postgres import create_all_tables, create_postgres_engine


def main() -> None:
    """连接 PostgreSQL 并创建 ORM 已定义表。"""
    engine = create_postgres_engine()
    if engine is None:
        print("未配置 DATABASE_URL，无法建表。")
        return
    create_all_tables(engine)
    print("PostgreSQL 表初始化完成（快捷模式）。生产请改用: alembic upgrade head")


if __name__ == "__main__":
    main()
