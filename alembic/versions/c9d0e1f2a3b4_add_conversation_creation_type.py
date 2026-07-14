"""add conversations creation_type

Revision ID: c9d0e1f2a3b4
Revises: b7c8d9e0f1a2
Create Date: 2026-07-13

【说明】
    增量迁移：conversations 表增加 creation_type（novel | video）。
"""

from alembic import op
import sqlalchemy as sa

from app.storage.postgres import postgres_constants as pc

revision = "c9d0e1f2a3b4"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None

_TABLE = pc.TABLE_CONVERSATIONS
_COLUMN = "creation_type"


def _column_exists(bind) -> bool:
    """检查 creation_type 列是否已存在。"""
    inspector = sa.inspect(bind)
    cols = [c["name"] for c in inspector.get_columns(_TABLE)]
    return _COLUMN in cols


def upgrade() -> None:
    """添加 creation_type 列（checkfirst）。"""
    bind = op.get_bind()
    if _column_exists(bind):
        return
    op.add_column(_TABLE, sa.Column(_COLUMN, sa.String(16), nullable=True))


def downgrade() -> None:
    """删除 creation_type 列。"""
    bind = op.get_bind()
    if not _column_exists(bind):
        return
    op.drop_column(_TABLE, _COLUMN)
