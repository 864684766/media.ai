"""Alembic 迁移环境配置。

【职责】
    从项目 DATABASE_URL 连接 PG，并对齐 ORM metadata。

【运行】
    poetry run alembic upgrade head
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.models.postgres.base import Base
from app.storage.postgres.orm_model_registry import register_all_orm_models
from app.storage.postgres.postgres_engine_factory import create_postgres_engine
from app.storage.postgres.postgres_settings_reader import get_postgres_url

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

register_all_orm_models()
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：仅输出 SQL。"""
    url = get_postgres_url() or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：连接 DATABASE_URL 执行迁移。"""
    engine = create_postgres_engine()
    if engine is None:
        section = config.get_section(config.config_ini_section, {})
        connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    else:
        connectable = engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
