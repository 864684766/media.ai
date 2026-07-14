"""initial schema baseline

Revision ID: f8a1c2b3d4e5
Revises:
Create Date: 2026-07-10

【说明】
    基线迁移：按当前 ORM 创建全部表（checkfirst）。
    已有 create_all_tables 的库可执行：alembic stamp f8a1c2b3d4e5
"""

from alembic import op

from app.models.postgres.base import Base
from app.storage.postgres.orm_model_registry import register_all_orm_models

revision = "f8a1c2b3d4e5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 ORM 定义的全部表（已存在则跳过）。"""
    register_all_orm_models()
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    """删除 ORM 定义的全部表（开发环境慎用）。"""
    register_all_orm_models()
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
